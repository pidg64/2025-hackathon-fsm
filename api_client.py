import os
import requests


class ApiClientError(Exception):
    """Custom exception for API client errors."""
    pass


class FileNotFoundError(Exception):
    """Custom exception for file not found errors."""
    pass


def _make_request(method, url, **kwargs):
    """Helper function to make HTTP requests and handle common errors."""
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise ApiClientError(f'Request to {url} failed: {e}') from e


def get_remote_name(rfid_url: str):
    try:
        response = _make_request('get', f'{rfid_url}/dequeue', timeout=5)
        return response.json().get('name')
    except ApiClientError:
        return None


def verify_face(face_verification_url: str, person_name: str):
    url = f'{face_verification_url}/verify_face/{person_name}'
    try:
        response = _make_request('get', url, timeout=60)
        data = response.json()
        if data.get('status') == 'Verified':
            return data.get('person')
    except ApiClientError as e:
        # A 404 is an expected 'not found' case. Only check for it if we have an HTTPError.
        if (
            isinstance(e.__cause__, requests.exceptions.HTTPError) and
            getattr(e.__cause__, 'response', None) is not None
        ):
            if e.__cause__.response.status_code == 404:
                return None  # It's a 404, treat as verification failure.        
        # For all other errors (like timeouts), re-raise the exception.
        raise
    return None


def start_recording(whisper_api_url: str):
    response = _make_request('post', f'{whisper_api_url}/start')
    return response.status_code == 200


def stop_recording(whisper_api_url: str):
    response = _make_request('post', f'{whisper_api_url}/stop')
    return response.json().get('transcription', '').strip()


def query_llm(llm_api_url: str, question: str):
    payload = {'question': question, 'language': 'en'}
    response = _make_request('post', llm_api_url, json=payload)
    return response.json().get('answer', '').strip()


def speak_text(tts_api_url: str, text: str):
    response = _make_request('post', tts_api_url, json={'text': text})
    return response.status_code == 200


def send_transcript(vlm_url: str, file_path: str):
    """
    Reads a transcript file and sends it as a file upload to the VLM service.

    Raises:
        ValueError: If vlm_url is not provided.
        FileNotFoundError: If the transcript file does not exist.
        ApiClientError: If the request to the VLM service fails.
    """
    if not vlm_url:
        raise ValueError('VLM URL must be provided.')

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise FileNotFoundError(f'Transcript file is missing or empty: {file_path}')

    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/plain')}
        _make_request('post', vlm_url, files=files)