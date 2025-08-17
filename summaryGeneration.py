from openai import OpenAI
from utils.airTableHelpers import getAllEntries, update_record
from loggerConfig import setup_logger
import time
import json
import os
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger()


client = OpenAI(api_key= os.getenv("openai_api_key"))

def get_llm_output(input_text: str, max_retries: int) -> dict:

    """
    Args:
        input_text (str): Candidate text.

    Returns:
        dict: Structured JSON with summary, score, and follow-ups.

    Function:
        This function queries the LLM with the input text and returns a structured JSON response.
        It retries on failure up to max_retries times with exponential backoff.
    """

    prompt = f"""
    You are an assistant evaluating candidate applications.
    Input text:
    \"\"\"{input_text}\"\"\"

    Please return ONLY a valid JSON object with fields:
    - "LLM Summary": A one-line summary of the candidate.
    - "LLM Score": An integer from 1-10.
    - "LLM Follow-Ups": A list of 2-3 follow-up questions.

    Example output:
    {{
      "LLM Summary": "Full-stack SWE with 5 yrs experience at Google and Meta",
      "LLM Score": 8,
      "LLM Follow-Ups": [
        "Can you confirm availability after next month?",
        "Have you led any production ML launches?"
      ]
    }}
    """

    output_text = ""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
            model = "gpt-4o-mini",   # You can swap with "gpt-4o" or "gpt-3.5-turbo"
            messages = [
                {"role": "system", "content": "You are a helpful evaluator that outputs only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0.3,
            max_tokens = 500,
            )

            # Extract and parse response
            output_text = response.choices[0].message.content.strip() # type: ignore
            # return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise e


    try:
        
        return json.loads(output_text)
    
    except Exception as e:
        return {"error": "Invalid JSON from model", "raw_output": output_text}
    

def updateLLMFieldsForRecords():

    '''Update LLM fields for all records with Compressed JSON filled out.
    Args:
        None

    Returns:
        None

    Function:
        This function retrieves all applicants, decompresses their compressed JSON data,
        queries the LLM for summary, score, and follow-ups, and updates the respective fields'''
    
    applicants = getAllEntries(filled = True)
    for app in applicants['records']:
        compressed_data = app["fields"].get("Compressed JSON")
        logger.info(f"Processing Applicant: {app['fields'].get('Applicant ID')}")
        openai_response = get_llm_output(compressed_data, max_retries=3)
        fields = ['LLM Summary', 'LLM Score', 'LLM Follow-Ups']
        for field in fields:
            try:
                update_record(app['id'], os.getenv('applicants_table_name'), field, openai_response[field])
                logger.info(f"Updated {field} for applicant {app['fields'].get('Applicant ID')}")

            except KeyError:
                logger.info(f"Field {field} not found in response for applicant {app['fields'].get('Applicant ID')}")

if __name__ == "__main__":
    # Run the function to update LLM fields for all records
    logger.info("Starting LLM field updates...")
    try:
        updateLLMFieldsForRecords()
        logger.info("LLM field updates completed successfully.")
    except Exception as e:
        logger.error(f"Error during LLM field updates: {e}")