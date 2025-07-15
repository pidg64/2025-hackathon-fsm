import logging
import api_client

from enum import Enum, auto

logger = logging.getLogger(__name__)
transcript_logger = logging.getLogger('transcript')


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()
    SPEAKING = auto()


class VoiceChatFSM:
    def __init__(
            self,
            user_name: str,
            whisper_api_url: str,
            llm_api_url: str,
            tts_api_url: str
        ):
        self.state = State.IDLE
        self.user_name = user_name
        self.whisper_api_url = whisper_api_url
        self.llm_api_url = llm_api_url
        self.tts_api_url = tts_api_url
        logger.info('Process started. Press SPACE to record or Q to quit.')
        logger.info(f'System session started for {user_name}.')

    def toggle(self):
        if self.state == State.IDLE:
            self._start_recording()
        elif self.state == State.RECORDING:
            self._stop_and_process()

    def _start_recording(self):
        logger.info('Starting recording.')
        try:
            if api_client.start_recording(self.whisper_api_url):
                self.state = State.RECORDING
            else:
                logger.error('Failed to start recording via API.')
        except api_client.ApiClientError as e:
            logger.error(f'Exception when starting recording: {e}')

    def _stop_and_process(self):
        logger.info('Stopping recording and processing.')
        self.state = State.PROCESSING
        try:
            transcription = api_client.stop_recording(self.whisper_api_url)
            if transcription:
                logger.info(f'Transcription: {transcription}')
                logger.info(f'{self.user_name}: {transcription}')
                self._query_llm(transcription)
            else:
                logger.warning('No text detected in transcription.')
                self.state = State.IDLE
        except api_client.ApiClientError as e:
            logger.error(f'Exception when stopping recording: {e}')
            self.state = State.IDLE

    def _query_llm(self, question: str):
        logger.info('Querying LLM.')
        transcript_logger.conversation(f'{self.user_name}: {question}')
        try:
            answer = api_client.query_llm(self.llm_api_url, question)
            if answer:
                logger.info(f'LLM Answer: {answer}')
                logger.info(f'Assistant: {answer}')
                transcript_logger.conversation(f'Assistant: {answer}')  
                self._speak_answer(answer)
            else:
                logger.error('Received no answer from LLM.')
                transcript_logger.conversation('Assistant: <No answer received>')
                self.state = State.IDLE
        except api_client.ApiClientError as e:
            logger.error(f'Exception querying LLM: {e}')
            self.state = State.IDLE

    def _speak_answer(self, text: str):
        logger.info('Generating audio with TTS...')
        self.state = State.SPEAKING
        try:
            if api_client.speak_text(self.tts_api_url, text):
                logger.info('Audio generated successfully.')
            else:
                logger.error('Failed to generate audio via TTS API.')
        except api_client.ApiClientError as e:
            logger.error(f'Exception in TTS: {e}')
        finally:
            self.state = State.IDLE