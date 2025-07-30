import os
from typing import Dict, Any
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    load_dotenv()
    
    return {
        'openai_base_url': os.getenv('OPENAI_BASE_URL'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'openai_model': os.getenv('OPENAI_MODEL'),
        'modelscope_api_key': os.getenv('OPENAI_API_KEY'),
        'tts_voice': os.getenv('TTS_VOICE', 'zh-CN-XiaoxiaoNeural'),  # Default to Chinese voice
    }