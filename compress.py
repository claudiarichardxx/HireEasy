from loggerConfig import setup_logger
from utils.airTableHelpers import *
import os
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger()

def updateCompressedJSONforRecords(records):

    '''
    Args:
        records (dict): Dictionary containing all records from the Applicants table.
        
    Returns:
        None
        
    Function:
        This function iterates through each record in the Applicants table, retrieves the relevant fields,
        and compresses them into a JSON format. It then updates the 'Compressed JSON' field for each record.
    '''
    
    for i in records['records']:

        compressed_json = {}
        logger.info(i['id'], i['fields'].get('Applicant ID', 'No ID'))

        for key, value in i['fields'].items():
            work = []
            if (key == 'Applicant ID'):
                compressed_json[key] = value

            elif (key == os.getenv('personal_details_table_name') or key == os.getenv('salary_preferences_table_name')):
                details = getRecordsById(value[0], key)
                personal_details = {}
                for field, entry in details['fields'].items():
                    if field not in ['Salary Preference ID', 'Created By']:
                        personal_details[field] = entry

                compressed_json[key] = personal_details
                

            elif (key == os.getenv('work_experience_table_name')):
                work_experience = []
                for id in value:
                    work = getRecordsById(id, key)

                    current_exp = {}
                    for field, entry in work['fields'].items():
                        if field not in ['Experience ID', 'Created By']:
                            current_exp[field] = entry

                    work_experience.append(current_exp)
                compressed_json[key] = work_experience
                
        update_record(i['id'], os.getenv('applicants_table_name'), 'Compressed JSON', compressed_json)


if __name__ == "__main__":

    logger.info("Starting compression of JSON for records...")
    try:
        records = getAllEntries(filled=True)
        updateCompressedJSONforRecords(records)
        logger.info("Compression completed successfully.")

    except Exception as e:
        logger.error(f"Error during compression: {e}")