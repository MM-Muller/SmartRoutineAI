import openai
import os
from typing import Dict, Optional
from datetime import datetime

class EmailSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the email summarizer.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will use OPENAI_API_KEY from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or provide it directly.")
        
        openai.api_key = self.api_key
    
    def summarize_email(self, email_text: str, max_tokens: int = 250, temperature: float = 0.7) -> Dict:
        """
        Summarize an email using OpenAI's GPT model.
        
        Args:
            email_text (str): The email text to summarize
            max_tokens (int): Maximum number of tokens in the summary
            temperature (float): Controls randomness in the output (0.0 to 1.0)
            
        Returns:
            Dict: Contains summary and metadata
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an email summarization assistant. Your task is to:
                        1. Extract key points from the email
                        2. Identify action items or requests
                        3. Highlight important dates or deadlines
                        4. Maintain a professional tone
                        5. Keep the summary concise and clear"""
                    },
                    {"role": "user", "content": email_text}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "model": "gpt-3.5-turbo",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "original_length": len(email_text),
                    "summary_length": len(summary)
                }
            }
            
        except openai.error.AuthenticationError:
            raise ValueError("Invalid OpenAI API key. Please check your credentials.")
        except openai.error.RateLimitError:
            raise Exception("OpenAI API rate limit exceeded. Please try again later.")
        except Exception as e:
            raise Exception(f"Error summarizing email: {str(e)}")
    
    def analyze_sentiment(self, email_text: str) -> Dict:
        """
        Analyze the sentiment of an email.
        
        Args:
            email_text (str): The email text to analyze
            
        Returns:
            Dict: Contains sentiment analysis results
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of this email. Consider tone, urgency, and emotional content."
                    },
                    {"role": "user", "content": email_text}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            sentiment = response.choices[0].message.content.strip()
            
            return {
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing sentiment: {str(e)}")

# Função de conveniência para uso rápido
def summarize_email(email_text: str, api_key: Optional[str] = None) -> str:
    """
    Convenience function to quickly summarize an email.
    
    Args:
        email_text (str): The email text to summarize
        api_key (str, optional): OpenAI API key
        
    Returns:
        str: The email summary
    """
    summarizer = EmailSummarizer(api_key)
    result = summarizer.summarize_email(email_text)
    return result["summary"] 