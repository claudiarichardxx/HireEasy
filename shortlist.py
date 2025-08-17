from utils.airTableHelpers import getAllEntries, add_record
from decompress import decompress_json
from loggerConfig import setup_logger
from datetime import datetime
logger = setup_logger()
import os
from dotenv import load_dotenv
load_dotenv()
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def calculate_experience(work_experiences):

    """
    Args:
        work_experiences (list): List of work experience dictionaries.
        
    Returns:
        float: Total years of experience rounded to 2 decimal places.
        
    Function:
        This function calculates the total years of experience from a list of work experience entries.
        It sums the days between start and end dates for each entry and converts it to years.
    """

    total_days = 0
    for exp in work_experiences:
        start_str = exp.get("Start")
        end_str = exp.get("End") or datetime.today().strftime("%Y-%m-%d") 
        
        if start_str and end_str:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
            total_days += (end_date - start_date).days
    
    total_years = total_days / 365
    return round(total_years, 2)


def shortlist_applicants():

    """
    Args:
        None
        
    Returns:
        None
        
    Function:
        This function retrieves all applicants from the Airtable, decompresses their JSON data,
        and checks if they meet the criteria for shortlisting based on experience, preferred rate,
        availability, and location. If they do, it adds them to the 'Shortlisted Leads' table.
    """
    
    applicants = getAllEntries(filled = True)

    for app in applicants['records']:

            compressed_data = app["fields"].get("Compressed JSON")
            logger.info(f"Processing Applicant: {app['fields'].get('Applicant ID')}")
            data = decompress_json(compressed_data)
            work_experience = data.get(os.getenv('work_experience_table_name'), [])
        
            years = calculate_experience(work_experience)
            
            companies_worked = [we.get("Company") for we in work_experience]
            if (years >= config['min_experience_years'] or any(company in config["tier_one_companies"] for company in companies_worked)):
                if (data.get(os.getenv('salary_preferences_table_name'))['Preferred Rate']<= config['max_preferred_rate'] and data.get(os.getenv('salary_preferences_table_name'))['Availability'] >= config['min_hours_available']):
                    if(data.get(os.getenv('personal_details_table_name'))['Location'] in config['location']):
                            logger.info(f"Shortlisting Applicant: {app['fields'].get('Applicant ID')}")

                            shortlisted_lead = {
                                "Applicant ID": [app['id']],
                                "Compressed JSON": compressed_data,
                                "Score Reason": f"Location: {data.get(os.getenv('personal_details_table_name'))['Location']}, Total Experience: {years} years, Companies: {companies_worked}, Preferred Rate: {data.get(os.getenv('salary_preferences_table_name'))['Preferred Rate']}, Availability: {data.get(os.getenv('salary_preferences_table_name'))['Availability']}",
                            }
                            add_record(os.getenv('shortlisted_leads_table_name'), shortlisted_lead)


if __name__ == "__main__":

    logger.info("Starting applicant shortlisting...")
    try:
        shortlist_applicants()
        logger.info("Shortlisting completed successfully.")
    except Exception as e:
        logger.error(f"Error during shortlisting: {e}")