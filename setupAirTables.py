from utils.dbModel import Applicants, PersonalDetails, WorkExperience, SalaryPreferences
from loggerConfig import setup_logger
import os
from dotenv import load_dotenv
load_dotenv()
logger = setup_logger()


def setup_airtables():

    """
    Args:
        None
    
    Returns:
        None

    Function:
        This function sets up the Airtable structure for the application by creating the necessary tables:
        - Applicants: Main table for applicants with fields for ID, compressed JSON, shortlist status, LLM summary, score, and follow-ups.
        - Personal Details: Linked to Applicants, contains full name, email, location, and LinkedIn profile.
        - Work Experience: Linked to Applicants, contains experience ID, company, title, start and end dates, and technologies.
        - Salary Preferences: Linked to Applicants, contains salary preference ID, preferred rate, and availability
    """
    
    try:
        # Create Applicants table
        applicants = Applicants()
        logger.info(f"Created Applicants table with ID: {applicants.parent_id}")

        # Create Personal Details table
        PersonalDetails(applicants.parent_id)
        logger.info(f"Created Personal Details table")

        # Create Work Experience table
        WorkExperience(applicants.parent_id)
        logger.info(f"Created Work Experience table")

        # Create Salary Preferences table
        SalaryPreferences(applicants.parent_id)
        logger.info(f"Created Salary Preferences table")

    except Exception as e:
        logger.error(f"Error setting up Airtables: {e}")


if __name__ == "__main__":

    logger.info("Starting Airtable setup...")
    try:
        setup_airtables()
        logger.info("Airtable setup completed successfully.")

    except Exception as e:
        logger.error(f"Error during Airtable setup: {e}")