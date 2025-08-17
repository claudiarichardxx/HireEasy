from loggerConfig import setup_logger
from dotenv import load_dotenv
import requests
import json
import os
load_dotenv()

airtable_token = os.getenv("airtable_token")
base_id = os.getenv("airtable_base_id")
headers = {'Authorization': f'Bearer {airtable_token}', 'Content-Type': 'application/json'}


logger = setup_logger()

def createAirTable(name, description, fields):

    """
    Args:
        name (str): The name of the table to create.
        description (str): A description of the table.
        fields (list): A list of dictionaries representing the fields in the table.

    Returns:
        dict: The response from the AirTable API.

    Function:
        This function creates a new table in AirTable with the specified name, description, and fields.
        It uses the AirTable API to create the table and returns the response.
    """

    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    # logger.info(url)
    data = {
        "name": name,
        "description": description,
        "fields": fields,
        
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def getAllEntries(filled = False):

    """
    Args:
        filled (bool): If True, returns only records with Compressed JSON filled out.
                       If False, returns all records.

    Returns:
        dict: All entries from the Applicants table.

    Function:
        This function retrieves all entries from the Applicants table in AirTable.
        If filled is True, it filters the records to return only those with Compressed JSON filled out.
        If filled is False, it returns all records regardless of the Compressed JSON field.  
    """

    formula = '{Compressed JSON} = ""' if not filled else '{Compressed JSON} != ""'

    url = f"https://api.airtable.com/v0/{base_id}/{os.getenv('applicants_table_name')}?filterByFormula={formula}"

    
    response = requests.get(url, headers=headers)

    return response.json()


def getRecordsById(record_id, table_name):

    """
    Args:
        record_id (str): The ID of the record to retrieve. 
        table_name (str): The name of the table to retrieve the record from.

    Returns:
        dict: The record with the specified ID from the specified table.

    Function:
        This function retrieves a record from a specified table in AirTable by its ID.
        It uses the AirTable API to get the record and returns the response.
    """

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"
    response = requests.get(url, headers=headers)
    
    return response.json()


def update_record(record_id, table_name, field, value):

    """
    Args:
        record_id (str): The ID of the record to update.
        table_name (str): The name of the table containing the record.
        field (str): The field to update.
        value (str or int): The new value for the field.
    
    Returns:
        dict: The updated record.
        
    Function:
        This function updates a specific field in a record within a specified table in AirTable.
        It uses the AirTable API to update the record and returns the updated record.
    """

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"

    if not (isinstance(value, str) or isinstance(value, int)):
        value = json.dumps(value) 
    
    data = {
        "fields": {
            field : value
        }
    }
    
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def add_record(table_name, value):

    """
    Args:
        table_name (str): The name of the table to add the record to.
        value (dict): The fields and values to add to the new record.
        
    Returns:
        dict: The response from the AirTable API with the newly created record.
        
    Function:
        This function adds a new record to a specified table in AirTable.
        It uses the AirTable API to create the record and returns the response.
    """
    try:
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"        
        response = requests.post(url, headers=headers, json={"fields" : value})
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.info(f"Error adding record to {table_name}: {e}")
        return None







