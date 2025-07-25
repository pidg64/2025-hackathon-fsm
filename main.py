import os
import sys
import time
import logging
import api_client

from pynput import keyboard
from dotenv import load_dotenv
from state_machine import VoiceChatFSM
from logging_config import setup_logging

load_dotenv()
setup_logging()

RFID_URL = os.getenv('RFID_URL', '')
LLM_API_URL = os.getenv('LLM_API_URL', '')
TTS_API_URL = os.getenv('TTS_API_URL', '')
WHISPER_API_URL = os.getenv('WHISPER_API_URL', '')
FACE_VERIFICATION_URL = os.getenv('FACE_VERIFICATION_URL', '')

logger = logging.getLogger(__name__)
transcript_logger = logging.getLogger('transcript')


def verify_identity():
    """Polls for a name and verifies identity via facial recognition."""
    logger.info('Waiting for name from the remote system')
    person = None
    while not person:
        person = api_client.get_remote_name(RFID_URL)
        time.sleep(1)
    logger.info(f'Name received: {person}. Verifying identity')
    while True:
        try:
            verified_person = api_client.verify_face(
                FACE_VERIFICATION_URL, person
            )
            if verified_person:
                logger.info(f'Identity verified for: {verified_person}')
                return verified_person
            else:
                logger.warning('Verification failed. Retrying detection')
        except api_client.ApiClientError as e:
            logger.error(f'An API error occurred during verification: {e}')        
        logger.info('Retrying facial verification\n')
        time.sleep(1)


def main():
    """Main application entry point."""
    try:
        skip_verification = '-s' in sys.argv or '--skip-verification' in sys.argv
        if skip_verification:
            logger.info('Skipping identity verification due to command-line argument.')
            person = os.getenv('USER', 'Luz')
        else:
            person = verify_identity()
        fsm = VoiceChatFSM(
            person,
            WHISPER_API_URL,
            LLM_API_URL,
            TTS_API_URL
        )
        def on_press(key):
            if key == keyboard.Key.space:
                fsm.toggle()
            elif hasattr(key, 'char') and key.char.lower() == 'q':
                logger.info('Session ended by user.')
                return False
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except Exception as e:
        logger.critical(f'A critical error occurred: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()