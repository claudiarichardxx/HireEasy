from utils.airTableHelpers import getAllEntries, add_record
from loggerConfig import setup_logger
import json
import os
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger()

def decompress_json(data):

    """
    Args:
        data (str): Compressed JSON string.

    Returns:
        dict: Decompressed JSON object.

    Function:
        This function attempts to decompress a JSON string into a Python dictionary.

    """
    
    try:
        return json.loads(data)
    
    except Exception as e:
        logger.info("Decompression failed:", e)
        return data
    
def fillChildTables():

    '''
    Args:
        None

    Returns:
        None

    Function:
        This function retrieves all applicants, decompresses their compressed JSON data,
        and adds the relevant fields to the respective child tables if they do not exist.
    '''

    try:
        applicants = getAllEntries(filled = True)
        for app in applicants['records']:
                compressed_data = app["fields"].get("Compressed JSON")
                logger.info(f"Processing Applicant: {app['fields'].get('Applicant ID')}")

                data = decompress_json(compressed_data)

                if os.getenv('personal_details_table_name') not in app['fields']:
                    add_record(os.getenv('personal_details_table_name'), data[os.getenv('personal_details_table_name')])

                if os.getenv('salary_preferences_table_name') not in app['fields']:
                    add_record(os.getenv('salary_preferences_table_name'), data[os.getenv('salary_preferences_table_name')])

                if os.getenv('work_experience_table_name') not in app['fields']:
                    for we in data[os.getenv('work_experience_table_name')]:
                        add_record(os.getenv('work_experience_table_name'), we)

    except Exception as e:
        logger.info(f"Error processing applicants: {e}")

if __name__ == "__main__":
    logger.info("Starting to backfill child tables...")
    try:
        fillChildTables()
        logger.info("Child tables filled successfully.")
    except Exception as e:
        logger.error(f"Error during filling child tables: {e}")