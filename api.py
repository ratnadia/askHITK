from fastapi import FastAPI
from pydantic import BaseModel
import json
import re

app = FastAPI()

# --- Helper function for normalizing query text ---
def normalize_text(text):
    if isinstance(text, str):
        text = re.sub(r'[\s\.\-\(\)&]+', '_', text.lower()).strip('_')
        return re.sub(r'_+', '_', text)
    return text

# --- Load Data ---
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    data = {"pyqs": {}, "timetables": {}, "faculty": {}, "holidays": {}}

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "College Helpdesk API is running."}

# --- PYQs Endpoint ---
@app.post("/pyqs")
def get_pyqs(query: Query):
    q = normalize_text(query.query)
    pyqs_data = data.get("pyqs", {}).get("deptpyq", [])

    # Extract all years in query (multiple possible)
    years = re.findall(r"20\d{2}", query.query)

    if not years:
        # Return all years
        return {"pyqs": {"DEPTPYQ": pyqs_data}}

    # Filter by years
    filtered = {y: pyqs_data.get(y, []) for y in years if y in pyqs_data}
    if filtered:
        return {"pyqs": {"DEPTPYQ": filtered}}
    return {"error": "No PYQs found for the given year(s)."}

# --- Timetable Endpoint ---
@app.post("/timetables")
def get_timetable(query: Query):
    general_link = data.get("timetables", {}).get("general_timetable_link")
    if general_link:
        return {
            "timetables": [{
                "program": "All Class Routines (External Link)",
                "link": general_link
            }]
        }
    return {"timetables": []}

# --- Faculty Endpoint ---
@app.get("/faculty")
def get_faculty_contacts():
    departments = data.get("faculty", {}).get("department_pages", [])
    if departments:
        return {"faculty": {"department_pages": departments}}
    return {"faculty": {"department_pages": []}}

# --- Holidays Endpoint ---
# --- Holidays Endpoint ---
@app.get("/holidays")
def get_holidays():
    holiday_link = data.get("holidays", {}).get("yearly_list_pdf")
    if holiday_link:
        return {
            "holidays": [
                {
                    "title": "Yearly Holiday List (PDF)",
                    "url": holiday_link
                }
            ]
        }
    # Always return a dictionary with 'holidays' key
    return {"holidays": []}
