from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.utils import *

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
