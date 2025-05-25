from __future__ import print_function
import os.path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopo necessário para criar eventos no Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'config/credentials.json'
TOKEN_FILE = 'config/token.json'

class CalendarError(Exception):
    """Exceção personalizada para erros do Google Calendar"""
    pass

def autenticar_google_calendar():
    """
    Autentica o usuário via OAuth2 e retorna um serviço da API do Google Calendar.
    
    Returns:
        googleapiclient.discovery.Resource: Serviço do Google Calendar autenticado
        
    Raises:
        CalendarError: Se houver erro na autenticação
    """
    try:
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise CalendarError("Arquivo de credenciais não encontrado. Por favor, configure suas credenciais do Google Calendar.")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        raise CalendarError(f"Erro na autenticação do Google Calendar: {str(e)}")

def criar_evento_google_calendar(titulo, data_hora_inicio, duracao_min=30, descricao=None, local=None, convidados=None):
    """
    Cria um evento no calendário principal do usuário.
    
    Args:
        titulo (str): Título do evento
        data_hora_inicio (datetime): Data e hora de início do evento
        duracao_min (int, optional): Duração do evento em minutos. Defaults to 30.
        descricao (str, optional): Descrição do evento. Defaults to None.
        local (str, optional): Local do evento. Defaults to None.
        convidados (list, optional): Lista de emails dos convidados. Defaults to None.
    
    Returns:
        str: URL do evento criado
        
    Raises:
        CalendarError: Se houver erro na criação do evento
    """
    try:
        service = autenticar_google_calendar()
        data_hora_fim = data_hora_inicio + timedelta(minutes=duracao_min)

        evento = {
            'summary': titulo,
            'start': {
                'dateTime': data_hora_inicio.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': data_hora_fim.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }

        # Adiciona campos opcionais se fornecidos
        if descricao:
            evento['description'] = descricao
        if local:
            evento['location'] = local
        if convidados:
            evento['attendees'] = [{'email': email} for email in convidados]

        evento = service.events().insert(calendarId='primary', body=evento).execute()
        return evento.get('htmlLink')
    except HttpError as e:
        raise CalendarError(f"Erro ao criar evento no Google Calendar: {str(e)}")
    except Exception as e:
        raise CalendarError(f"Erro inesperado ao criar evento: {str(e)}")

def listar_eventos_google_calendar(data_inicio=None, data_fim=None, max_resultados=10):
    """
    Lista eventos do calendário principal do usuário.
    
    Args:
        data_inicio (datetime, optional): Data de início para filtrar eventos. Defaults to None.
        data_fim (datetime, optional): Data de fim para filtrar eventos. Defaults to None.
        max_resultados (int, optional): Número máximo de eventos a retornar. Defaults to 10.
    
    Returns:
        list: Lista de eventos encontrados
        
    Raises:
        CalendarError: Se houver erro ao listar eventos
    """
    try:
        service = autenticar_google_calendar()
        
        # Se não fornecidas, usa o período de hoje até 7 dias
        if not data_inicio:
            data_inicio = datetime.now()
        if not data_fim:
            data_fim = data_inicio + timedelta(days=7)
            
        eventos = service.events().list(
            calendarId='primary',
            timeMin=data_inicio.isoformat(),
            timeMax=data_fim.isoformat(),
            maxResults=max_resultados,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return eventos.get('items', [])
    except HttpError as e:
        raise CalendarError(f"Erro ao listar eventos do Google Calendar: {str(e)}")
    except Exception as e:
        raise CalendarError(f"Erro inesperado ao listar eventos: {str(e)}")

def deletar_evento_google_calendar(evento_id):
    """
    Deleta um evento do calendário.
    
    Args:
        evento_id (str): ID do evento a ser deletado
        
    Raises:
        CalendarError: Se houver erro ao deletar o evento
    """
    try:
        service = autenticar_google_calendar()
        service.events().delete(calendarId='primary', eventId=evento_id).execute()
    except HttpError as e:
        raise CalendarError(f"Erro ao deletar evento do Google Calendar: {str(e)}")
    except Exception as e:
        raise CalendarError(f"Erro inesperado ao deletar evento: {str(e)}")
