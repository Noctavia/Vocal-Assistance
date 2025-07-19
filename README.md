# 🤖 Assistant Vocal de Bureau avec IA

> Un assistant vocal intelligent capable d'exécuter des commandes système et de converser naturellement en français.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Fonctionnalités

### 🎤 **Reconnaissance Vocale**
- **Vosk** : Reconnaissance vocale locale haute performance
- **SpeechRecognition** : Fallback avec Google Speech API
- **Écoute continue** en arrière-plan
- **Mots de réveil** : "assistant", "ordinateur", "hey assistant"

### 🤖 **Intelligence Artificielle**
- **Ollama + LangChain** pour conversations naturelles
- **Mémoire conversationnelle** entre les interactions
- **Réponses contextuelles** en français
- **Mode local** - pas de données envoyées au cloud

### 💻 **Commandes Système**
- **Applications** : Notepad, calculatrice, navigateur, explorateur, terminal
- **Multimédia** : Lecture de musique, Spotify, YouTube
- **Système** : Verrouillage, extinction, redémarrage, contrôle volume
- **Cross-platform** : Windows, macOS, Linux

### 🔊 **Synthèse Vocale**
- **pyttsx3** avec voix française automatique
- **Feedback vocal** pour toutes les actions
- **Vitesse et volume** configurables

## 🚀 Installation

### Prérequis
- Python 3.9 ou plus récent
- Microphone et haut-parleurs
- Ollama installé (pour l'IA)

### Installation des dépendances

```bash
# Packages Python essentiels
pip install SpeechRecognition pyttsx3 langchain ollama vosk

# PyAudio (peut nécessiter des étapes spéciales selon l'OS)
pip install pyaudio
```

#### 🔧 Installation PyAudio par OS

**Windows :**
```bash
# Si pip ne marche pas, télécharger le wheel depuis :
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
```

**macOS :**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian) :**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Installation Ollama

```bash
# Télécharger depuis https://ollama.ai
# Puis installer un modèle français
ollama pull llama2
# ou pour de meilleures performances en français :
ollama pull mistral
```

### Modèle Vosk (optionnel mais recommandé)

1. Télécharger un modèle français : https://alphacephei.com/vosk/models
2. Recommandé : `vosk-model-fr-0.6-linto-2.2.0`
3. Extraire dans le dossier du projet
4. Modifier le chemin dans le code si nécessaire

## 🎯 Utilisation

### Lancement
```bash
python assistant_vocal.py
```

### Interface
```
🤖 ASSISTANT VOCAL DÉMARRÉ
💡 Dites 'assistant' pour me réveiller
💡 Tapez 'quit' pour quitter
💡 Tapez 'help' pour voir les commandes
```

### Utilisation vocale
1. **Réveil** : Dites "assistant" pour activer l'écoute
2. **Commande** : Énoncez votre commande ou question
3. **Réponse** : L'assistant exécute et répond vocalement

### Commandes disponibles

#### 📱 Applications
```
"Ouvrir notepad"          → Lance le bloc-notes
"Ouvrir calculatrice"     → Lance la calculatrice
"Ouvrir navigateur"       → Ouvre le navigateur web
"Ouvrir explorateur"      → Lance l'explorateur de fichiers
"Ouvrir terminal"         → Ouvre un terminal
```

#### 🎵 Multimédia
```
"Jouer musique"           → Lit un fichier audio
"Ouvrir Spotify"          → Lance Spotify
"Ouvrir YouTube"          → Ouvre YouTube dans le navigateur
```

#### ⚙️ Système
```
"Volume up/down"          → Contrôle le volume
"Couper son"              → Active/désactive le son
"Verrouiller ordinateur"  → Verrouille la session
"Éteindre ordinateur"     → Extinction programmée
"Redémarrer ordinateur"   → Redémarrage programmé
```

#### 🤖 Assistant
```
"Arrêter écoute"          → Désactive l'écoute (réveil avec "assistant")
"Aide"                    → Affiche l'aide
"Quitter assistant"       → Ferme le programme
```

#### 💬 Conversation IA
```
"Quel temps fait-il ?"    → Question météo
"Raconte-moi une blague"  → Conversation naturelle
"Comment ça va ?"         → Interaction sociale
"Explique-moi..."         → Questions techniques
```

## ⚙️ Configuration

### Personnalisation des mots de réveil
```python
self.wake_words = ["assistant", "ordinateur", "hey jarvis", "salut"]
```

### Changement du modèle IA
```python
self.llm = Ollama(model="mistral", base_url="http://localhost:11434")
```

### Ajout de nouvelles commandes
```python
self.system_commands.update({
    'ouvrir code': self.open_vscode,
    'ouvrir steam': self.open_steam,
})
```

## 🛠️ Architecture

```
assistant_vocal.py
├── VocalAssistant (classe principale)
├── Recognition (Vosk + SpeechRecognition)
├── TTS (pyttsx3)
├── AI (Ollama + LangChain)
└── SystemCommands (commandes OS)
```

### Composants principaux
- **`init_speech_recognition()`** : Initialise Vosk ou SpeechRecognition
- **`init_text_to_speech()`** : Configure pyttsx3 avec voix française
- **`init_ai_model()`** : Connecte Ollama avec mémoire conversationnelle
- **`process_speech()`** : Traite la parole reconnue
- **`handle_command()`** : Route vers commandes système ou IA

## 🐛 Dépannage

### L'assistant ne répond pas
- Vérifiez que le microphone fonctionne
- Essayez de dire plus fort "assistant"
- Regardez les logs dans la console

### Erreur PyAudio
```bash
# Réinstallez avec la méthode appropriée à votre OS
# Voir section "Installation PyAudio par OS"
```

### Ollama non disponible
- Vérifiez qu'Ollama est lancé : `ollama serve`
- Testez : `ollama run llama2`
- L'assistant fonctionne sans IA (commandes uniquement)

### Vosk non trouvé
- L'assistant utilise SpeechRecognition en fallback
- Téléchargez un modèle français pour de meilleures performances

### Commandes système ne marchent pas
- Vérifiez les permissions
- Certaines commandes nécessitent des droits admin

## 🔒 Sécurité et Confidentialité

- **IA locale** : Conversations traitées par Ollama en local
- **Pas de cloud** : Aucune donnée envoyée sur internet (sauf Google Speech si Vosk indisponible)
- **Commandes système** : Soyez prudent avec les commandes d'extinction/redémarrage
- **Permissions** : L'assistant peut accéder aux applications système

## 🤝 Contribution

1. Fork le projet
2. Créez une branche : `git checkout -b ma-fonctionnalite`
3. Commitez : `git commit -am 'Ajout de ma fonctionnalité'`
4. Push : `git push origin ma-fonctionnalite`
5. Créez une Pull Request

### Idées d'amélioration
- [ ] Interface graphique (Tkinter/PyQt)
- [ ] Support de plus de langues
- [ ] Intégration avec plus d'applications
- [ ] Commandes personnalisées par utilisateur
- [ ] Plugin system
- [ ] Reconnaissance de visage pour sécurité
- [ ] API REST pour contrôle distant

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Vosk** pour la reconnaissance vocale locale
- **Ollama** pour l'IA locale
- **pyttsx3** pour la synthèse vocale
- **LangChain** pour l'orchestration IA
- Communauté Python pour les excellentes librairies

## 📞 Support

- 🐛 **Issues** : [GitHub Issues](https://github.com/votre-repo/assistant-vocal/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/votre-repo/assistant-vocal/discussions)
- 📧 **Email** : votre.email@example.com

---

<div align="center">
<strong>Fait avec ❤️ en Python</strong><br>
<em>Assistant vocal intelligent pour tous</em>
</div>
