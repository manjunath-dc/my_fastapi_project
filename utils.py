import pandas as pd
from langchain import OpenAI
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("LLM_API_KEY is not set in the environment variables.")
        self.llm = OpenAI(api_key=self.api_key)
    
    def classify(self, description: str) -> str:
        try:
            prompt = f"Is the following company a technology company? {description}"
            response = self.llm.complete(prompt)
            if "yes" in response.lower():
                return "Yes"
            else:
                return "No"
        except Exception as e:
            logger.error(f"Error interacting with LLM: {e}")
            return "Unknown"

def parse_csv(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise

def add_technology_column(df: pd.DataFrame) -> pd.DataFrame:
    llm_client = LLMClient()
    if "Description" not in df.columns:
        logger.error("CSV does not contain 'Description' column.")
        raise ValueError("CSV does not contain 'Description' column.")
    
    df["Technology Company"] = df["Description"].apply(llm_client.classify)
    return df
