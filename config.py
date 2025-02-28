import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint  
from langchain_core.language_models import BaseLLM

# Load environment variables
load_dotenv()

# Initialize Storage Directory
BASE_DIR = "./data_storage"
os.makedirs(BASE_DIR, exist_ok=True)

def get_llm() -> BaseLLM:
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not api_token:
        raise ValueError("❌ Missing Hugging Face API Token!")
    
    try:
        return HuggingFaceEndpoint(
            repo_id="deepseek-ai/deepseek-llm-r1-7b",  
            huggingfacehub_api_token=api_token,
            temperature=0.7,
            max_length=12000,  
            task="text-generation"
        )
    except Exception as e:
        raise ValueError(f"Error initializing LLM: {str(e)}")

llm = get_llm()
