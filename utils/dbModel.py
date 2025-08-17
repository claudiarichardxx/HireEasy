from utils.airTableHelpers import createAirTable
from loggerConfig import setup_logger
import os

from dotenv import load_dotenv
load_dotenv()


logger = setup_logger()


class Applicants:

    def __init__(self):
        self.name = os.getenv("applicants_table_name", "Applicants")
        self.description = "Table for applicants"
        self.fields = [
            {"name": "Applicant ID", "type": "email"},  
            {"name": "Compressed JSON", "type": "multilineText"},
            {"name": "Shortlist Status", "type": "checkbox", "options": {
                                                                        "color": "greenBright",
                                                                        "icon": "check"
                                                                        }},
            {"name": "LLM Summary", "type": "multilineText"},
            {"name": "LLM Score", "type": "number", "options": {"precision": 2}},
            {"name": "LLM Follow-Ups", "type": "multilineText"}
        ]
        returned = createAirTable(self.name, self.description, self.fields)
        logger.info(returned)
        logger.info(returned.get('primaryFieldId', None))
        self.parent_id = returned.get('id', None)


class PersonalDetails:

    def __init__(self, parent_id):
        self.name = os.getenv("personal_details_table_name", "Personal Details")
        self.description = "Table for personal details"
        self.fields = [
            {"name": "Full Name", "type": "singleLineText"},
            {"name": "Applicant ID", "type": "multipleRecordLinks", "options": {"linkedTableId": parent_id}},
            {"name": "Email", "type": "email"},
            {"name": "Location", "type": "multilineText"},
            {"name": "LinkedIn Profile", "type": "url"}
        ]
        returned = createAirTable(self.name, self.description, self.fields)
        logger.info(returned)

class WorkExperience:

    def __init__(self, parent_id):
        self.name = os.getenv("work_experience_table_name", "Work Experience")
        self.description = "Table for work experience"
        self.fields = [
            {"name": "Experience ID", "type": "number", "options": {"precision": 0}},
            {"name": "Applicant ID",  "type": "multipleRecordLinks", "options": {"linkedTableId": parent_id}},
            {"name": "Company", "type": "singleLineText"},
            {"name": "Title", "type": "singleLineText"},
            {"name": "Start", "type": "date", "options": {"dateFormat": {"name": "local"} }},
            {"name": "End", "type": "date", "options": {"dateFormat": {"name": "local"} }},
            {"name": "Technologies", "type": "multilineText"}
        ]
        returned = createAirTable(self.name, self.description, self.fields)
        logger.info(returned)

class SalaryPreferences:

    def __init__(self, parent_id):
        self.name = os.getenv("salary_preferences_table_name", "Salary Preferences")
        self.description = "Table for salary preferences"
        self.fields = [
            {"name": "Salary Preference ID", "type": "number", "options": {"precision": 0}},
            {"name": "Applicant ID", "type": "multipleRecordLinks", "options": {"linkedTableId": parent_id}},
            {"name": "Preferred Rate", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
            {"name": "Minimum Rate", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
            {"name": "Currency", "type": "singleLineText"},
            {"name": "Availability", "type": "singleLineText"}
        ]
        returned = createAirTable(self.name, self.description, self.fields)
        logger.info(returned)


class ShortlistedLeads:

    def __init__(self, parent_id):
        self.name = os.getenv("shortlisted_leads_table_name", "Shortlisted Leads")
        self.description = "Table for shortlisted leads"
        self.fields = [
            {"name": "Lead ID", "type": "number", "options": {"precision": 0}},
            {"name": "Applicant ID", "type": "multipleRecordLinks", "options": {"linkedTableId": parent_id}},
            {"name": "Compressed JSON", "type": "richText"},
            {"name": "Score Reason", "type": "multilineText"},
            {"name": "Created At", "type": "dateTime", "options": {"timeZone" : "America/Toronto","dateFormat": {"name" : "local"}, "timeFormat": {"name" : "12hour"}}}  
        ]
        returned = createAirTable(self.name, self.description, self.fields)
        logger.info(returned)