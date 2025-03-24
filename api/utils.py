import fitz
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
fetch DATA from the TEXT above, in below format given and then return json data file.
and make sure to return a json with all square brackets and curly braces closed so that i can convert it to json.
"""
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
      "new_survey_number":,
      "old_survey_number":,
      "sub_division":,
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
"""
'''

def get_prompt(pdf_text:str):
    return query_template.replace("<=<=<=<=<=<pdf_text>=>=>=>=>=>", pdf_text, 1)

def extract_text_from_pdf(pdf_bytes:bytes):
    with fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def get_response(prompt:str):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[f'''{prompt}'''],
        config=types.GenerateContentConfig(
            temperature=0.1
        )
    )
    return response

def fetch_json(pdf_bytes):
    pdf_text = extract_text_from_pdf(pdf_bytes)
    prompt = get_prompt(pdf_text)
    response = get_response(prompt)
    start_str = "```json"
    end_str = "```"
    start = response.text.find(start_str)+len(start_str)
    end = response.text.find(end_str, start)
    if start>-1 and end>-1:
      result = json.loads(response.text[start:end])
    else:
        result = {}
    return result