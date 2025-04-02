import pdfplumber
from google import genai
from google.genai import types
import os
import io
import json
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
query_template = f'''
"""
<=<=<=<=<=<pdf_text>=>=>=>=>=>
"""
'''

def get_prompt(pdf_text:str):
    return query_template.replace("<=<=<=<=<=<pdf_text>=>=>=>=>=>", pdf_text, 1)

def extract_text_from_pdf(pdf_bytes:bytes):
    ordered_content = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            elements = []

            tables = page.extract_tables()
            for table in tables:
                for i in range(len(table[0])):
                   if table[0][i]==None and i>0:
                      table[0][i]=table[0][i-1]
                   if isinstance(table[0][i], str):
                      table[0][i] = table[0][i].replace("\n", " ")
                for i in range(len(table)):
                   if i==0: continue
                   for j in range(len(table[i])):
                      if isinstance(table[i][j], str):
                        table[i][j] = table[i][j].replace("\n", " ")
                      if table[i][j]==None:
                         table[i][j] = "\t"
                   print(table[i])
                elements.append({"type": "table", "content": "\n".join("|".join(t) for t in table)})

            text = page.extract_text()
            if text:
                elements.append({"type": "text", "content": text.strip()})

            ordered_content.append({
                "page_number": page_num,
                "elements": elements
            })
    return ordered_content

def get_pdf_text(ordered_content:list):
   main_text = ""
   for i in ordered_content:
      main_text+=f"page number - {i['page_number']}\n"
      for el in i["elements"]:
         main_text+=f"type - {el['type']}\t content - \n"
         main_text+=f"{el['content']}\n\n\n"
      main_text+="\n\n\n"
   return main_text.strip()


def get_response(prompt:str):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
           system_instruction=f'''
fetch DATA from the TEXT and TABLE given, TABLE's row are separated by lines and columns are separated with | this vertical bar (pipe), in below format given and then return json data file.
And make sure to return a json with all square brackets and curly braces closed so that i can convert it to json.
Also if you do not found any text above or land details in that text or property related documents then simply return json with {{"document_type": null}} only.

Format - 
{{
  "document_type":,
  "office":,
  "district":,
  "taluk":,
  "village":,   
  "survey_number":,
  "owners": [
    {{
      "name":
    }},
    {{
      "name":
    }},
    {{
      "name":
    }},
    {{
      "name":
    }}
  ],
  "land_details": [
    {{
      "sur_field":,
      "sub_division":,
      "new_survey_number":,
      "old_survey_number":,
      "land_type":,
      "area_hectare":,
      "area_acre":,
      "area_sqft":,
      "registration_date":
    }}
  ],
  "official_verification": {{
    "verified_by":,
    "date":,
    "time":
  }},
  "notes": []
}}
''',
           temperature=0.1
        ),
        contents=[f'''{prompt}''']
    )
    return response

def fetch_json(pdf_bytes):
    try:
      pdf_text = extract_text_from_pdf(pdf_bytes)
      pdf_text = get_pdf_text(pdf_text)
      prompt = get_prompt(pdf_text)
      response = get_response(prompt)
      start_str = "```json"
      end_str = "```"
      start = response.text.find(start_str)+len(start_str)
      end = response.text.find(end_str, start)
      if start>-1 and end>-1:
        result = json.loads(response.text[start:end])
        try:
          land_details = dict(result).get("land_details")
          def is_valid_land_detail(land):
              return any(value is not None for key, value in land.items() if key != "registration_date")
          any_valid = any(is_valid_land_detail(land) for land in land_details)
          if any_valid==False:
             result = {"document_type": None}
        except Exception as e:
          result = {"document_type": None}
      else:
          result = {"document_type": None}
    except Exception as e:
        result = {"error_occ": e}
    return result