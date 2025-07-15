# Configure logging
import logging


CONVERSATION_LEVEL_NUM = 25
logging.addLevelName(CONVERSATION_LEVEL_NUM, 'CONVERSATION')

def conversation(self, message, *args, **kws):
    if self.isEnabledFor(CONVERSATION_LEVEL_NUM):
        self._log(CONVERSATION_LEVEL_NUM, message, args, **kws)

logging.Logger.conversation = conversation

def setup_logging():
    """Configures logging for console and a dedicated transcript file."""
    TRANSCRIPT_LOG_FILE = 'transcript.log'
    verbose_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    transcript_formatter = logging.Formatter('%(asctime)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(verbose_formatter)
    root_logger.addHandler(console_handler)
    transcript_logger = logging.getLogger('transcript')
    transcript_logger.setLevel(CONVERSATION_LEVEL_NUM)    
    transcript_handler = logging.FileHandler(TRANSCRIPT_LOG_FILE)
    transcript_handler.setFormatter(transcript_formatter)
    transcript_logger.addHandler(transcript_handler)
    transcript_logger.propagate = False
