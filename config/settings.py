"""
Carrega essas variáveis com os.environ ou via dotenv, e as centraliza para o resto do projeto.
"""
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configurações gerais
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY")
IDIOMA_PADRAO = os.getenv("IDIOMA_PADRAO", "pt-BR")
DEBUG = os.getenv("DEBUG", "False") == "True"
