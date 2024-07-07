import json
import os
from elevenlabs import Voice, save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from pydub.silence import split_on_silence
from .config import Config


class AudioGenerator:
    def __init__(self, config: Config):
        self.config = config

    async def generate_audio_files(self, subject: str, length: float = 1):
        # Creează directoarele pentru audio
        os.makedirs(f"./output/{subject}/voices", exist_ok=True)
        if length <= 1:
            os.makedirs(f"./output/{subject}/voices/edited", exist_ok=True)

        with open(f"output/{subject}/script.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            audio_prompts = list(dict(data)["script"])

        for i, prompt in enumerate(audio_prompts):
            self._generate_audio_from_prompt(prompt, subject, i)

        if length <= 1:
            self._silence_audio(subject)

    def _generate_audio_from_prompt(self, prompt: str, subject: str, iteration: int):
        client = ElevenLabs(
            api_key=self.config.ELEVENLABS_API_KEY,
        )
        audio = client.generate(
            text=prompt,
            voice=Voice(voice_id="Nhs6IYoAcBwjSVy82OUS"),
            model="eleven_multilingual_v2",
        )
        os.makedirs(f"./output/{subject}/voices", exist_ok=True)

        save(audio, f"./output/{subject}/voices/{iteration + 1}.mp3")

    def _silence_audio(self, subject: str):
        input_folder = f"./output/{subject}/voices"
        output_folder = f"./output/{subject}/voices/edited"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file_name in os.listdir(input_folder):
            if file_name.endswith(".mp3"):
                input_path = os.path.join(input_folder, file_name)
                output_file_name = f"{os.path.splitext(file_name)[0]}_silenced.mp3"
                output_path = os.path.join(output_folder, output_file_name)

                sound = AudioSegment.from_mp3(input_path)
                audio_chunks = split_on_silence(
                    sound, min_silence_len=100, silence_thresh=-45, keep_silence=50
                )

                combined = AudioSegment.empty()
                for chunk in audio_chunks:
                    combined += chunk

                combined.export(output_path, format="mp3")
