#!/usr/bin/env python3
"""
Assistant Vocal de Bureau avec IA
Fonctionnalités:
- Reconnaissance vocale avec Vosk
- Commandes système (ouvrir programmes, fichiers, musique)
- Conversation IA avec Ollama/LangChain
- Synthèse vocale avec pyttsx3
"""

import json
import os
import sys
import threading
import time
import subprocess
import platform
import webbrowser
from pathlib import Path
import queue

# Imports pour la reconnaissance vocale
import vosk
import pyaudio
import speech_recognition as sr

# Synthèse vocale
import pyttsx3

# IA et traitement du langage
from langchain.llms import Ollama
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

class VocalAssistant:
    def __init__(self):
        self.is_listening = False
        self.is_running = True
        self.audio_queue = queue.Queue()
        
        # Configuration audio
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Initialisation des composants
        self.init_speech_recognition()
        self.init_text_to_speech()
        self.init_ai_model()
        self.init_system_commands()
        
        # Mots de réveil
        self.wake_words = ["assistant", "ordinateur", "hey assistant", "salut"]
        
        print("🤖 Assistant vocal initialisé avec succès!")
        self.speak("Assistant vocal prêt. Dites 'assistant' pour me réveiller.")

    def init_speech_recognition(self):
        """Initialise la reconnaissance vocale avec Vosk"""
        try:
            # Téléchargez un modèle Vosk français depuis https://alphacephei.com/vosk/models
            model_path = "vosk-model-fr-0.6-linto-2.2.0"  # Ajustez le chemin
            
            if not os.path.exists(model_path):
                print("⚠️  Modèle Vosk non trouvé. Utilisation de speech_recognition...")
                self.use_vosk = False
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
            else:
                self.vosk_model = vosk.Model(model_path)
                self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, self.RATE)
                self.use_vosk = True
                print("✅ Vosk initialisé avec succès")
                
        except Exception as e:
            print(f"❌ Erreur Vosk: {e}")
            self.use_vosk = False
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

    def init_text_to_speech(self):
        """Initialise la synthèse vocale"""
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            
            # Cherche une voix française
            for voice in voices:
                if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.8)
            print("✅ Synthèse vocale initialisée")
            
        except Exception as e:
            print(f"❌ Erreur TTS: {e}")
            self.tts_engine = None

    def init_ai_model(self):
        """Initialise le modèle IA avec Ollama"""
        try:
            # Assurez-vous qu'Ollama est installé et qu'un modèle est disponible
            self.llm = Ollama(model="llama2", base_url="http://localhost:11434")
            
            # Mémoire conversationnelle
            self.memory = ConversationBufferMemory()
            self.conversation = ConversationChain(
                llm=self.llm,
                memory=self.memory,
                verbose=False
            )
            
            # Test de connexion
            try:
                test_response = self.llm("Dis bonjour en français")
                print("✅ IA Ollama connectée")
            except:
                print("⚠️  Ollama non disponible, mode commandes uniquement")
                self.llm = None
                
        except Exception as e:
            print(f"❌ Erreur IA: {e}")
            self.llm = None

    def init_system_commands(self):
        """Initialise les commandes système"""
        self.system_commands = {
            # Applications courantes
            'ouvrir notepad': self.open_notepad,
            'ouvrir calculatrice': self.open_calculator,
            'ouvrir navigateur': self.open_browser,
            'ouvrir explorateur': self.open_explorer,
            'ouvrir terminal': self.open_terminal,
            
            # Média
            'jouer musique': self.play_music,
            'arrêter musique': self.stop_music,
            'ouvrir spotify': self.open_spotify,
            'ouvrir youtube': self.open_youtube,
            
            # Système
            'verrouiller ordinateur': self.lock_computer,
            'éteindre ordinateur': self.shutdown_computer,
            'redémarrer ordinateur': self.restart_computer,
            'volume up': self.volume_up,
            'volume down': self.volume_down,
            'couper son': self.mute_volume,
            
            # Contrôle assistant
            'arrêter écoute': self.stop_listening,
            'quitter assistant': self.quit_assistant,
            'aide': self.show_help
        }

    def speak(self, text):
        """Synthèse vocale"""
        print(f"🤖 Assistant: {text}")
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass

    def listen_continuous(self):
        """Écoute continue avec Vosk ou speech_recognition"""
        if self.use_vosk:
            self.listen_with_vosk()
        else:
            self.listen_with_sr()

    def listen_with_vosk(self):
        """Écoute avec Vosk"""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        print("🎤 Écoute avec Vosk...")
        
        while self.is_running:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                if self.vosk_rec.AcceptWaveform(data):
                    result = json.loads(self.vosk_rec.Result())
                    text = result.get('text', '').strip()
                    if text:
                        self.process_speech(text)
                        
            except Exception as e:
                print(f"Erreur audio: {e}")
                time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def listen_with_sr(self):
        """Écoute avec speech_recognition"""
        print("🎤 Écoute avec speech_recognition...")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while self.is_running:
            try:
                with self.microphone as source:
                    # Écoute courte pour détecter les mots de réveil
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio, language='fr-FR')
                    self.process_speech(text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Erreur reconnaissance: {e}")
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"Erreur écoute: {e}")
                time.sleep(0.1)

    def process_speech(self, text):
        """Traite la parole reconnue"""
        text_lower = text.lower().strip()
        print(f"🎯 Reconnu: {text}")
        
        # Vérification mot de réveil
        if not self.is_listening:
            for wake_word in self.wake_words:
                if wake_word in text_lower:
                    self.is_listening = True
                    self.speak("Oui, je vous écoute.")
                    return
            return
        
        # Traitement des commandes
        self.handle_command(text_lower)

    def handle_command(self, text):
        """Traite les commandes"""
        # Vérification commandes système
        for command, action in self.system_commands.items():
            if command in text:
                action()
                return
        
        # Si pas de commande système, utiliser l'IA
        if self.llm:
            self.handle_ai_conversation(text)
        else:
            self.speak("Je n'ai pas compris cette commande. Dites 'aide' pour voir les commandes disponibles.")

    def handle_ai_conversation(self, text):
        """Gère la conversation avec l'IA"""
        try:
            # Ajout du contexte français
            prompt = f"Réponds en français de manière naturelle et concise: {text}"
            response = self.conversation.predict(input=prompt)
            self.speak(response)
        except Exception as e:
            print(f"Erreur IA: {e}")
            self.speak("Désolé, je ne peux pas traiter votre demande pour le moment.")

    # === COMMANDES SYSTÈME ===
    
    def open_notepad(self):
        """Ouvre le bloc-notes"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["notepad.exe"])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-a", "TextEdit"])
            else:  # Linux
                subprocess.run(["gedit"])
            self.speak("Bloc-notes ouvert")
        except Exception as e:
            self.speak("Impossible d'ouvrir le bloc-notes")

    def open_calculator(self):
        """Ouvre la calculatrice"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["calc.exe"])
            elif platform.system() == "Darwin":
                subprocess.run(["open", "-a", "Calculator"])
            else:
                subprocess.run(["gnome-calculator"])
            self.speak("Calculatrice ouverte")
        except Exception as e:
            self.speak("Impossible d'ouvrir la calculatrice")

    def open_browser(self):
        """Ouvre le navigateur"""
        webbrowser.open("https://www.google.com")
        self.speak("Navigateur ouvert")

    def open_explorer(self):
        """Ouvre l'explorateur de fichiers"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer.exe"])
            elif platform.system() == "Darwin":
                subprocess.run(["open", "."])
            else:
                subprocess.run(["nautilus"])
            self.speak("Explorateur ouvert")
        except Exception as e:
            self.speak("Impossible d'ouvrir l'explorateur")

    def open_terminal(self):
        """Ouvre le terminal"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["cmd.exe"])
            elif platform.system() == "Darwin":
                subprocess.run(["open", "-a", "Terminal"])
            else:
                subprocess.run(["gnome-terminal"])
            self.speak("Terminal ouvert")
        except Exception as e:
            self.speak("Impossible d'ouvrir le terminal")

    def play_music(self):
        """Joue de la musique"""
        try:
            # Cherche des fichiers audio dans le dossier Musique
            music_dir = Path.home() / "Music"
            if not music_dir.exists():
                music_dir = Path.home() / "Musique"
            
            if music_dir.exists():
                audio_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))
                if audio_files:
                    if platform.system() == "Windows":
                        os.startfile(str(audio_files[0]))
                    else:
                        subprocess.run(["open" if platform.system() == "Darwin" else "xdg-open", str(audio_files[0])])
                    self.speak("Musique lancée")
                else:
                    self.speak("Aucun fichier musical trouvé")
            else:
                self.speak("Dossier musique non trouvé")
        except Exception as e:
            self.speak("Impossible de jouer la musique")

    def stop_music(self):
        """Arrête la musique"""
        # Cette fonction nécessiterait une intégration plus complexe avec les lecteurs média
        self.speak("Arrêt de la musique non implémenté")

    def open_spotify(self):
        """Ouvre Spotify"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["spotify.exe"], shell=True)
            else:
                subprocess.run(["spotify"])
            self.speak("Spotify ouvert")
        except Exception as e:
            webbrowser.open("https://open.spotify.com")
            self.speak("Spotify Web ouvert")

    def open_youtube(self):
        """Ouvre YouTube"""
        webbrowser.open("https://www.youtube.com")
        self.speak("YouTube ouvert")

    def lock_computer(self):
        """Verrouille l'ordinateur"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif platform.system() == "Darwin":
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
            else:
                subprocess.run(["gnome-screensaver-command", "--lock"])
            self.speak("Ordinateur verrouillé")
        except Exception as e:
            self.speak("Impossible de verrouiller l'ordinateur")

    def shutdown_computer(self):
        """Éteint l'ordinateur"""
        self.speak("Extinction de l'ordinateur dans 10 secondes")
        try:
            if platform.system() == "Windows":
                subprocess.run(["shutdown", "/s", "/t", "10"])
            else:
                subprocess.run(["sudo", "shutdown", "-h", "+1"])
        except Exception as e:
            self.speak("Impossible d'éteindre l'ordinateur")

    def restart_computer(self):
        """Redémarre l'ordinateur"""
        self.speak("Redémarrage de l'ordinateur dans 10 secondes")
        try:
            if platform.system() == "Windows":
                subprocess.run(["shutdown", "/r", "/t", "10"])
            else:
                subprocess.run(["sudo", "reboot"])
        except Exception as e:
            self.speak("Impossible de redémarrer l'ordinateur")

    def volume_up(self):
        """Augmente le volume"""
        try:
            if platform.system() == "Windows":
                # Nécessite le package pycaw pour Windows
                self.speak("Contrôle volume Windows non implémenté")
            elif platform.system() == "Darwin":
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
                self.speak("Volume augmenté")
            else:
                subprocess.run(["amixer", "set", "Master", "5%+"])
                self.speak("Volume augmenté")
        except Exception as e:
            self.speak("Impossible de modifier le volume")

    def volume_down(self):
        """Diminue le volume"""
        try:
            if platform.system() == "Darwin":
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
                self.speak("Volume diminué")
            else:
                subprocess.run(["amixer", "set", "Master", "5%-"])
                self.speak("Volume diminué")
        except Exception as e:
            self.speak("Impossible de modifier le volume")

    def mute_volume(self):
        """Coupe le son"""
        try:
            if platform.system() == "Darwin":
                subprocess.run(["osascript", "-e", "set volume with output muted"])
                self.speak("Son coupé")
            else:
                subprocess.run(["amixer", "set", "Master", "toggle"])
                self.speak("Son basculé")
        except Exception as e:
            self.speak("Impossible de couper le son")

    def stop_listening(self):
        """Arrête l'écoute active"""
        self.is_listening = False
        self.speak("Je n'écoute plus. Dites 'assistant' pour me réveiller.")

    def quit_assistant(self):
        """Quitte l'assistant"""
        self.speak("Au revoir!")
        self.is_running = False

    def show_help(self):
        """Affiche l'aide"""
        help_text = """Commandes disponibles:
        - Applications: ouvrir notepad, calculatrice, navigateur, explorateur, terminal
        - Média: jouer musique, ouvrir spotify, youtube
        - Système: verrouiller ordinateur, volume up/down, couper son
        - Assistant: arrêter écoute, quitter assistant
        - Vous pouvez aussi me poser des questions!"""
        
        print(help_text)
        self.speak("Liste des commandes affichée dans la console")

    def run(self):
        """Lance l'assistant vocal"""
        try:
            # Lance l'écoute dans un thread séparé
            listen_thread = threading.Thread(target=self.listen_continuous, daemon=True)
            listen_thread.start()
            
            print("\n" + "="*50)
            print("🤖 ASSISTANT VOCAL DÉMARRÉ")
            print("="*50)
            print("💡 Dites 'assistant' pour me réveiller")
            print("💡 Tapez 'quit' pour quitter")
            print("💡 Tapez 'help' pour voir les commandes")
            print("="*50 + "\n")
            
            # Interface console pour les commandes manuelles
            while self.is_running:
                try:
                    user_input = input().strip().lower()
                    if user_input == 'quit':
                        self.quit_assistant()
                    elif user_input == 'help':
                        self.show_help()
                    elif user_input:
                        self.handle_command(user_input)
                        
                except KeyboardInterrupt:
                    self.quit_assistant()
                    break
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"Erreur fatale: {e}")
        finally:
            print("🔴 Assistant vocal arrêté")

def main():
    """Point d'entrée principal"""
    print("🚀 Initialisation de l'assistant vocal...")
    
    # Vérifications des dépendances
    required_packages = ['vosk', 'pyaudio', 'pyttsx3', 'speech_recognition', 'langchain']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'speech_recognition':
                import speech_recognition as sr
            else:
                __import__(package)
        except ImportError:
            missing_packages.append('SpeechRecognition' if package == 'speech_recognition' else package)
    
    if missing_packages:
        print(f"❌ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install " + " ".join(missing_packages))
        return
    
    # Lancement de l'assistant
    assistant = VocalAssistant()
    assistant.run()

if __name__ == "__main__":
    main()
