import os
import openai
from dotenv import load_dotenv


def get_mysql_config():
    return {
        "host": "localhost",
        "port": 3306,
        "user": "pantry_user",
        "password": "MyStrongPwd123!",
        "database": "smart_pantry",
    }


def get_openai():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return  openai.api_key 
