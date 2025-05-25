import pyttsx3
from typing import Optional

class VoiceOutput:
    def __init__(self, rate: int = 180, voice: str = 'brazil'):
        """
        Initialize the voice output system.
        
        Args:
            rate (int): Speech rate (words per minute)
            voice (str): Voice identifier
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        
        # Try to set the specified voice, fallback to first available if not found
        try:
            self.engine.setProperty('voice', voice)
        except Exception:
            if voices:
                self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text: str, wait: bool = True) -> None:
        """
        Speak the given text.
        
        Args:
            text (str): Text to be spoken
            wait (bool): Whether to wait for speech to complete
        """
        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {str(e)}")
    
    def stop(self) -> None:
        """Stop any ongoing speech."""
        try:
            self.engine.stop()
        except Exception as e:
            print(f"Error stopping speech: {str(e)}")

# Função de conveniência para uso rápido
def speak_text(text: str, rate: Optional[int] = None, voice: Optional[str] = None) -> None:
    """
    Convenience function to quickly speak text.
    
    Args:
        text (str): Text to be spoken
        rate (int, optional): Speech rate
        voice (str, optional): Voice identifier
    """
    voice_output = VoiceOutput(rate=rate if rate is not None else 180,
                             voice=voice if voice is not None else 'brazil')
    voice_output.speak(text)
