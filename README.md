
# 🎧 Ecoute

Ecoute is a live transcription tool that provides real-time transcripts for both the user's microphone input (You) and the user's speakers output (Speaker) in a textbox.

## Sponsored By: Recall.ai - Meeting Transcription API

If you’re working with speech detection or transcription for meetings, consider checking out [Recall.ai](https://www.recall.ai/product/meeting-transcription-api/?utm_source=github&utm_medium=sponsorship&utm_campaign=sevask-ecoute), an API that works with Zoom, Google Meet, Microsoft Teams, and more. Recall.ai diarizes by pulling the speaker data and separate audio streams from the meeting platforms, which means 100% accurate speaker diarization with actual speaker names and speaker emails.

## 📖 Demo

https://github.com/user-attachments/assets/5616421f-838d-439f-8b15-0df7b8d33459

Ecoute is designed to help users in their conversations by providing live transcriptions.

## 🚀 Getting Started

Follow these steps to set up and run Ecoute on your local machine.

### 📋 Prerequisites

- Python >=3.8.0
- (Optional) An OpenAI API key that can access Whisper API (set up a paid account OpenAI account)
- Windows OS (Not tested on others)
- FFmpeg 

If FFmpeg is not installed in your system, you can follow the steps below to install it.

First, you need to install Chocolatey, a package manager for Windows. Open your PowerShell as Administrator and run the following command:
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Once Chocolatey is installed, you can install FFmpeg by running the following command in your PowerShell:
```
choco install ffmpeg
```
Please ensure that you run these commands in a PowerShell window with administrator privileges. If you face any issues during the installation, you can visit the official Chocolatey and FFmpeg websites for troubleshooting.

### 🔧 Installation

1. Clone the repository:

   ```
   git clone https://github.com/SevaSk/ecoute
   ```

2. Navigate to the `ecoute` folder:

   ```
   cd ecoute
   ```

3. Install the required packages:

   It is highly recommended to use a virtual environment:
   ```powershell
   # 1. Create a virtual environment
   python -m venv venv

   # 2. Activate the virtual environment
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate

   # 3. Install packages
   pip install -r requirements.txt
   ```

   *If you get a launcher path error (like `Fatal error in launcher`), bypass it by running pip directly through the python executable:*
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
   
4. (Optional) Create a `keys.py` file in the `ecoute` directory and add your API keys:

   Create the `keys.py` file manually in the root folder and enter the following:
   
   ```python
   OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
   GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
   ```
   *(This file is configured in `.gitignore` so your API keys will stay safe and local on your machine).*

### 🎬 Running Ecoute

To run the main script, make sure your virtual environment is active and run:

```powershell
python main.py
```

**Troubleshooting / Direct Run:**
If your global Python environment is broken or you don't want to activate the virtual environment, you can run the app directly using the `venv` path:

```powershell
.\venv\Scripts\python.exe main.py
```

For a better and faster version that also works with most languages, use:

```powershell
python main.py --api
```

*(Or direct run: `.\venv\Scripts\python.exe main.py --api`)*

Upon initiation, Ecoute will begin transcribing your microphone input and speaker output in real-time. Please note that it might take a few seconds for the system to warm up (or to download the Faster-Whisper model on the first run) before the transcription becomes real-time.

The --api flag will use the whisper api for transcriptions. This significantly enhances transcription speed and accuracy, and it works in most languages (rather than just English without the flag). It's expected to become the default option in future releases. However, keep in mind that using the Whisper API will consume more OpenAI credits than using the local model. This increased cost is attributed to the advanced features and capabilities that the Whisper API provides. Despite the additional expense, the substantial improvements in speed and transcription accuracy may make it a worthwhile investment for your use case.

### ⚠️ Limitations

While Ecoute provides real-time transcription and response suggestions, there are several known limitations to its functionality that you should be aware of:

**Default Mic and Speaker:** Ecoute is currently configured to listen only to the default microphone and speaker set in your system. It will not detect sound from other devices or systems. If you wish to use a different mic or speaker, you will need to set it as your default device in your system settings.

**Whisper Model**: If the --api flag is not used, we utilize the 'tiny' version of the Whisper ASR model, due to its low resource consumption and fast response times. However, this model may not be as accurate as the larger models in transcribing certain types of speech, including accents or uncommon words.

**Language**: If you are not using the --api flag the Whisper model used in Ecoute is set to English. As a result, it may not accurately transcribe non-English languages or dialects. We are actively working to add multi-language support to future versions of the program.

## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve Ecoute.
