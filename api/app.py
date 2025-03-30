from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
# from typing import Optional
from api.utils import *

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail={"msg": "Only PDF files are allowed"})
        file_ = await file.read()
        response = fetch_json(file_)
        if response=={}:
            raise HTTPException(status_code=400, detail={"msg": "Data not found"})
        return {"filename": file.filename, "content_type": file.content_type, "json_data":response}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"msg": e})

@app.post("/patta/view/otpgenerate/")
async def get_otp(
    mobileNo: str | None = None, 
):
    try:
        url = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
        params = {
            "page": "CaptchaArith",
            "jsoncallback": "?"
        }
        response = requests.post(url, params=params)

        url = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
        params = {
            "page": "otpgenerate",
            "mobileno": mobileNo,
            "actionid": "AC01",
            "lan": "ta",
            "jsoncallback": "?"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://eservices.tn.gov.in/",
            "Origin": "https://eservices.tn.gov.in",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        otpres = json.loads(requests.post(url, data=params, headers=headers).text)
        if otpres["statusCode"]!='true':
            raise HTTPException(status_code=500, detail={"msg": "Server down"})
        return {"msg": "Success"}


    except Exception as e:
        raise HTTPException(status_code=400, detail={"msg": e})

@app.post("/patta/view/patta/")
async def get_patta_view(
    district: str, 
    taluk: str, 
    village: str, 
    landType: str,
    optionNo: int, 
    mobileNo: str, 
    otpNo: str, 
    pattaNo: str | None = None, 
    surveyNo: str | None = None, 
    subdivNo: str | None = None, 
    pattaName: str | None = None, 
):
    try:

        url = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
        params = {
            "page": "verify_otp",
            "mobileno": mobileNo,
            "otpno": otpNo,
            "jsoncallback": "?"
        }
        otpverifyres = json.loads(requests.post(url, params=params).text)
        if otpverifyres["statusCode"]!="true":
            raise HTTPException(403, detail={"msg": "Wrong OTP"})
        
        url = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
        params = {
            "page": "ruralservice",
            "ser": "dist",
            "lang": "ta",
            "type": "rur",
            "call_type": "ser"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://eservices.tn.gov.in/",
            "Origin": "https://eservices.tn.gov.in",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        dis = json.loads(requests.post(url, data=params, headers=headers).text)
        dcode=None
        for d in dis:
            if district==d["dname"] or district==d["dtname"]:
                dcode = d["dcode"]
        if dcode==None: raise HTTPException(status_code=401, detail = {"msg": "District name not found"})


        url = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
        params = {
            "page": "ruralservice",
            "ser": "tlk",
            "distcode": dcode,
            "lang": "ta",
            "type": "rur",
            "call_type": "ser"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://eservices.tn.gov.in/",
            "Origin": "https://eservices.tn.gov.in",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        tcode = None
        tlks = json.loads(requests.post(url, data=params, headers=headers).text)
        for t in tlks:
            if taluk==t["ttname"] or taluk==t["tname"]:
                tcode = t["tcode"]
                tnflag = t["nflag"]
        if tcode==None: raise HTTPException(status_code=401, detail = {"msg": "Taluk name not found"})
        
        url = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
        params = {
            "page": "ruralservice",
            "ser": "vill",
            "distcode": dcode,
            "talukcode": tcode,
            "lang": "ta",
            "type": "rur",
            "call_type": "ser"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://eservices.tn.gov.in/",
            "Origin": "https://eservices.tn.gov.in",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br"
        }
        vills = json.loads(requests.post(url, data=params, headers=headers).text)
        vcode = None
        for vill in vills:
            if village==vill["villagename"] or village==vill["villagetname"]:
                vcode = vill["villagecode"]
        if vcode==None: raise HTTPException(status_code=401, detail = {"msg": "District name not found"})

        if optionNo<1 and optionNo>3:
            raise HTTPException(status_code=401, detail = {"msg": "Option number not found"})


        url = "https://eservices.tn.gov.in/eservicesnew/land/chittaExtract_ta.html?lan=ta"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://eservices.tn.gov.in/"
        }
        if "r" in landType or "R" in landType:
            ltype = "R"
        elif "n" in landType or "N" in landType:
            ltype = "N"
        if optionNo==1:
            if pattaName==None:
                pattaName=""
            data = {
                "task": "chittaTam",
                "searchpattano": "no",
                "chkrno": None,
                "districtCode": dcode,
                "talukCode": f"{tcode}/{tnflag}",
                "villageCode": vcode,
                "viewOpt": "pt",
                "landType": ltype,
                "pattaNo": pattaNo,
                "searchPattaName": pattaName,
                "surveyNo": "",
                "subdivNo": "",
                "mobileno": mobileNo,
                "mobileno_ver": mobileNo,
                "otpno": otpNo,
                "otpno_ver": otpNo
            }
        elif optionNo==2:
            subdivurl = "https://eservices.tn.gov.in/eservicesnew/land/ajax.html"
            subdivparams = {
                "page": "getSubdivNo",
                "districtCode": dcode,
                "talukCode": f"{tcode}/{tnflag}",
                "villageCode": vcode,
                "surveyno": surveyNo,
                "landtype": ltype,
                "flag": "F"
            }
            subdivheaders = {
                "Origin": "https://eservices.tn.gov.in",
                "Referer": "https://eservices.tn.gov.in/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Content-Length": "0",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            if subdivNo in requests.post(subdivurl, params=subdivparams, headers=subdivheaders).text:
                pass
            else:
                raise HTTPException(status_code=403, detail={"msg": "Sub Division not found"})

            data = {
                "task": "chittaTam",
                "searchpattano": "no",
                "chkrno": None,
                "districtCode": dcode,
                "talukCode": f"{tcode}/{tnflag}",
                "villageCode": vcode,
                "viewOpt": "sur",
                "landtype": landType,
                "pattaNo": "",
                "searchPattaName": "",
                "surveyNo": surveyNo,
                "subdivNo": subdivNo,
                "mobileno": mobileNo,
                "mobileno_ver": mobileNo,
                "otpno": otpNo,
                "otpno_ver": otpNo
            }
        elif optionNo==3:
            data = {
                "task": "chittaTam",
                "searchpattano": "no",
                "chkrno": None,
                "districtCode": dcode,
                "talukCode": f"{tcode}/{tnflag}",
                "villageCode": vcode,
                "viewOpt": "searchptno",
                "pattaNo": "",
                "searchPattaName": pattaName,
                "surveyNo": "",
                "subdivNo": "",
                "mobileno": mobileNo,
                "mobileno_ver": mobileNo,
                "otpno": otpNo,
                "otpno_ver": otpNo
            }
        response = requests.post(url, headers=headers, data=data)
        return {"response": response.text}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"msg": e})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
