import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url',
    default=("https://amalnathrmca-3030.theiadockern"
             "ext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai")
)
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="https://sentianalyzer.1k8zyj7pmen'g.us-south.codeengine.appdomain.cloud/"
)

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Add code for get requests to back end
def get_request(endpoint, **kwargs):
    params = "&".join(f"{key}={value}" for key, value in kwargs.items())
    request_url = f"{backend_url}{endpoint}?{params}"
    logger.info(f"GET from {request_url}")

    try:
        response = requests.get(request_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
    except Exception as err:
        logger.error(f"Unexpected error: {err}")

    return None


# Add code for retrieving sentiments
def analyze_review_sentiments(text):
    base_url = (
       "https://sentianalyzer.1k8zyj7pmeng.us-south.codeengine.appdomain.cloud/analyze/"
    )
    request_url = base_url + requests.utils.quote(
        text
    )  # Encode the text to handle spaces and special characters

    try:
        response = requests.get(request_url)
        response.raise_for_status()  # Ensure we catch HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
    except Exception as err:
        logger.error(f"Unexpected error: {err}")

    return None


# Add code for posting review
def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        logger.info(response.json())
        return response.json()
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
    except Exception as err:
        logger.error(f"Unexpected error: {err}")

    return None
