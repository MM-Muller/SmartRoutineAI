import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY")
IDIOMA_PADRAO = os.getenv("IDIOMA_PADRAO", "pt-BR")
DEBUG = os.getenv("DEBUG", "False") == "True"
