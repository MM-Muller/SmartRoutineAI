import speech_recognition as sr
import time
from typing import Optional, Tuple

class VoiceInputError(Exception):
    """Exceção personalizada para erros de entrada de voz"""
    pass

class VoiceRecognizer:
    def __init__(self, language: str = "pt-BR", timeout: int = 5, phrase_time_limit: int = 10):
        """
        Inicializa o reconhecedor de voz.
        
        Args:
            language (str): Idioma para reconhecimento. Defaults to "pt-BR".
            timeout (int): Tempo máximo de espera para início da fala em segundos. Defaults to 5.
            phrase_time_limit (int): Tempo máximo de duração da fala em segundos. Defaults to 10.
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Ajusta para ruído ambiente
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000  # Ajuste conforme necessário
        
    def calibrar_microfone(self) -> None:
        """
        Calibra o microfone para o ambiente atual.
        Ajusta o threshold de energia baseado no ruído ambiente.
        """
        try:
            with sr.Microphone() as source:
                print("🎙️ Calibrando microfone... Aguarde 2 segundos.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("✅ Calibração concluída!")
        except Exception as e:
            raise VoiceInputError(f"Erro ao calibrar microfone: {str(e)}")
    
    def ouvir_comando(self, mostrar_feedback: bool = True) -> Tuple[str, float]:
        """
        Captura e reconhece o comando de voz.
        
        Args:
            mostrar_feedback (bool): Se True, mostra mensagens de feedback. Defaults to True.
            
        Returns:
            Tuple[str, float]: Texto reconhecido e confiança do reconhecimento
            
        Raises:
            VoiceInputError: Se houver erro no reconhecimento
        """
        try:
            with sr.Microphone() as source:
                if mostrar_feedback:
                    print("🎙️ Aguardando comando de voz...")
                
                # Captura o áudio
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                if mostrar_feedback:
                    print("🎯 Processando...")
                
                # Reconhece o áudio
                resultado = self.recognizer.recognize_google(
                    audio,
                    language=self.language,
                    show_all=True  # Retorna todos os resultados possíveis
                )
                
                if not resultado or not resultado.get('alternative'):
                    raise VoiceInputError("Não foi possível reconhecer o áudio.")
                
                # Pega o resultado com maior confiança
                melhor_resultado = resultado['alternative'][0]
                texto = melhor_resultado['transcript']
                confianca = melhor_resultado.get('confidence', 0.0)
                
                if mostrar_feedback:
                    print(f"✅ Reconhecido: {texto}")
                    print(f"📊 Confiança: {confianca:.2%}")
                
                return texto, confianca
                
        except sr.WaitTimeoutError:
            raise VoiceInputError("Tempo de espera esgotado. Nenhum áudio detectado.")
        except sr.UnknownValueError:
            raise VoiceInputError("Não foi possível entender o áudio.")
        except sr.RequestError as e:
            raise VoiceInputError(f"Erro na requisição ao serviço de reconhecimento: {str(e)}")
        except Exception as e:
            raise VoiceInputError(f"Erro inesperado: {str(e)}")
    
    def reconhecer_comando_loop(self, max_tentativas: int = 3) -> Optional[str]:
        """
        Tenta reconhecer um comando de voz várias vezes.
        
        Args:
            max_tentativas (int): Número máximo de tentativas. Defaults to 3.
            
        Returns:
            Optional[str]: Texto reconhecido ou None se todas as tentativas falharem
        """
        for tentativa in range(max_tentativas):
            try:
                texto, confianca = self.ouvir_comando()
                
                # Se a confiança for muito baixa, tenta novamente
                if confianca < 0.6:
                    print(f"⚠️ Baixa confiança ({confianca:.2%}). Tentando novamente...")
                    continue
                    
                return texto
                
            except VoiceInputError as e:
                print(f"❌ Tentativa {tentativa + 1}/{max_tentativas}: {str(e)}")
                if tentativa < max_tentativas - 1:
                    print("🔄 Tentando novamente em 2 segundos...")
                    time.sleep(2)
                continue
                
        print("❌ Todas as tentativas falharam.")
        return None

# Exemplo de uso
if __name__ == "__main__":
    try:
        reconhecedor = VoiceRecognizer()
        reconhecedor.calibrar_microfone()
        
        while True:
            comando = reconhecedor.reconhecer_comando_loop()
            if comando:
                print(f"Comando reconhecido: {comando}")
                if comando.lower() in ["sair", "parar", "encerrar"]:
                    print("👋 Encerrando reconhecimento de voz...")
                    break
                    
    except KeyboardInterrupt:
        print("\n👋 Programa encerrado pelo usuário.")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")