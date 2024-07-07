import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        self.SD_API_KEY = os.getenv("SD_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        self.AUDIO_DIR = os.path.join(self.RESOURCES_DIR, 'audio')
        self.PROMPTS_DIR = os.path.join(self.RESOURCES_DIR, 'prompts')
        self.SOUNDTRACK_PATH = os.path.join(self.AUDIO_DIR, 'soundtrack.mp3')
        self.SOUNDTRACK_EDITED_PATH = os.path.join(self.AUDIO_DIR, 'soundtrack_edited.mp3')
        self.SYSTEM_PROMPT_FILE = os.path.join(self.PROMPTS_DIR, 'prompt.txt')
        self.USED_SUBJECTS_FILE = os.path.join(self.PROMPTS_DIR, 'used_subjects.txt')
