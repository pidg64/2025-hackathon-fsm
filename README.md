# Voice-Controlled AI Assistant

This project is a voice-controlled AI assistant that uses a finite state machine (FSM) to manage interactions. It integrates several microservices for functionalities like speech-to-text, language model querying, and text-to-speech.

## Project Structure

- `main.py`: The main entry point of the application. It handles user identity verification and keyboard inputs.
- `state_machine.py`: Implements the core logic of the voice chat using a finite state machine.
- `api_client.py`: A client to interact with the various external API services (Whisper, LLM, TTS, etc.).
- `logging_config.py`: Configures the application's logging, separating technical logs from the conversation transcript.
- `queue_server.py`: A simple FastAPI server to simulate an external system that provides user names for verification.
- `requirements.txt`: A list of all the Python dependencies required for this project.

## Prerequisites

- Python 3.8+
- `pip` for package management

## Setup and Installation

1. **Clone the repository (if you haven't already):**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Create and activate a virtual environment:**

   This is recommended to keep project dependencies isolated.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
4. **Create the environment configuration file:**

   Create your own local configuration.

   ```bash
   touch .env
   ```

   Now, edit the `.env` file and fill in the correct URLs for your local or remote services:

   ```env
   WHISPER_API_URL="http://127.0.0.1:8001"
   LLM_API_URL="http://127.0.0.1:8000/rag/ask"
   TTS_API_URL="http://127.0.0.1:5001/post-message"
   RFID_URL="http://127.0.0.1:8081"
   FACE_VERIFICATION_URL="http://127.0.0.1:8002"
   ```

## How to Run the Application

You need to run two separate processes in two different terminals.

### Terminal 1: Start the Queue Server

This server simulates an external service that provides user names for verification.

```bash
uvicorn queue_server:app --host 0.0.0.0 --port 8081
```

### Terminal 2: Start the Main Application

This is the main voice assistant application.

```bash
python3 main.py
```

## How to Use

1. **Trigger the user verification:**

   Once the main application is running, it will wait for a name from the queue server. To provide a name, open a web browser or use a tool like `curl` to send a request to the queue server.

   ```bash
   curl -X POST http://127.0.0.1:8081/enqueue/Diego
   ```

   The main application will pick up the name "Diego" and proceed to the (simulated) face verification step.
2. **Interact with the assistant:**

   - **Press the `SPACE` bar** to start recording your voice.
   - **Release the `SPACE` bar** to stop recording and send your speech for processing.
   - The assistant will respond with a spoken answer.
   - **Press `q`** at any time to quit the application gracefully.

## Logging

- **Console:** All technical logs (`INFO`, `WARNING`, `ERROR`) are printed to the console.
- **`transcript.log`:** A clean, machine-readable transcript of the conversation between the user and the assistant is saved here. This file is designed to be used as input for other processes, such as summarization.
