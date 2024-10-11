from datetime import datetime
import uuid
from config import config
import os


def generate_conversation_id():
    return f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"


def get_conversation_folder(conversation_id):
    return os.path.join(config.UPLOAD_FOLDER, conversation_id)
