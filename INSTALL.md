# Installation Guide

This guide provides detailed instructions for installing the AI Voice Assistant on different operating systems.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Basic Installation

1. Clone the repository:
   ```
   git clone https://github.com/amrpyt/ai-voice-assistant.git
   cd ai-voice-assistant
   ```

2. Create a virtual environment:
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install basic dependencies:
   ```
   pip install -r requirements.txt
   ```

## Platform-Specific Dependencies

### PyAudio Installation

PyAudio is required for microphone input but can be tricky to install on some platforms.

#### Windows
```
pip install pipwin
pipwin install pyaudio
```

#### macOS
```
brew install portaudio
pip install pyaudio
```

#### Linux (Ubuntu/Debian)
```
sudo apt-get update
sudo apt-get install python3-pyaudio
```

### Sounddevice Installation

If you encounter issues with sounddevice:

#### Windows
```
pip install sounddevice
```

#### macOS/Linux
```
pip install sounddevice
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'sounddevice'**
   - Make sure you've installed the sounddevice package: `pip install sounddevice`

2. **PyAudio installation fails**
   - Try using pipwin on Windows: `pip install pipwin && pipwin install pyaudio`
   - On Linux, install system dependencies: `sudo apt-get install portaudio19-dev python3-pyaudio`

3. **Text-to-speech not working**
   - Ensure pyttsx3 is installed: `pip install pyttsx3`
   - On Linux, you might need additional packages: `sudo apt-get install espeak`

## Configuration

After installation, create a `.env` file based on the provided `.env.example` to configure the application settings.

## Running the Application

```
python run_assistant.py
```