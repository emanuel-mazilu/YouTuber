import json
import os
import glob
from moviepy.editor import AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, TextClip, \
    concatenate_videoclips
from natsort import natsorted
from pydub import AudioSegment, effects
from .utils import wrap_text
from PIL import Image
import numpy as np


class VideoCreator:
    def __init__(self, config):
        self.config = config

    async def generate_video(self, subject: str, length: float):
        width, height = (768, 1344) if length <= 1 else (1344, 768)
        fps = 24

        clips = self._create_image_clips(subject, length)
        audio = self._create_audio(subject, length)
        text_clips = self._create_text_clips(subject, length, width, height)

        concat_clip = concatenate_videoclips(clips, method="compose")
        concat_clip = CompositeVideoClip([concat_clip] + text_clips)
        concat_clip = concat_clip.set_duration(audio.duration).set_audio(audio)

        os.makedirs("./final_videos", exist_ok=True)
        concat_clip.write_videofile(f"./final_videos/{subject}.mp4", fps=fps)

    def _create_image_clips(self, subject: str, length: float):
        file_list = natsorted(glob.glob(f"./output/{subject}/images/*.png"))
        image_duration = length * 60 / len(file_list)
        return [ImageClip(m).set_duration(image_duration) for m in file_list]

    def _create_audio(self, subject: str, length: float):
        if length <= 1:
            audio_files = natsorted(glob.glob(f"./output/{subject}/voices/edited/*.mp3"))
        else:
            audio_files = natsorted(glob.glob(f"./output/{subject}/voices/*.mp3"))

        audio_segments = [AudioSegment.from_mp3(file) for file in audio_files]
        voiceover = sum(audio_segments)
        voiceover = effects.normalize(voiceover)
        voiceover_path = f"./output/{subject}/voiceover.mp3"
        voiceover.export(voiceover_path, format="mp3")
        voiceover = AudioFileClip(voiceover_path)

        background_music = AudioSegment.from_mp3(self.config.SOUNDTRACK_PATH)
        background_music = effects.normalize(background_music)
        background_music = background_music - 20
        background_music = background_music[5 * 1000:(voiceover.duration + 5) * 1000]
        background_music = background_music.fade_in(2000).fade_out(2000)
        background_music_path = self.config.SOUNDTRACK_EDITED_PATH
        background_music.export(background_music_path, format="mp3")
        background_music = AudioFileClip(background_music_path).set_duration(voiceover.duration)

        return CompositeAudioClip([background_music, voiceover])

    def _create_text_clips(self, subject: str, length: float, width: int, height: int):
        with open(f"output/{subject}/script.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            text_segments = list(dict(data)["script"])

        text_clips = []
        current_time = 0
        max_chars_per_line = 30 if length <= 1 else 50
        max_lines_per_clip = 2

        for i, segment in enumerate(text_segments):
            wrapped_text = wrap_text(segment, max_chars_per_line)
            lines = wrapped_text.split("\n")
            num_clips = (len(lines) + max_lines_per_clip - 1) // max_lines_per_clip

            audio_file = f"./output/{subject}/voices/{'edited/' if length <= 1 else ''}{i + 1}_silenced.mp3"
            audio_duration = AudioSegment.from_mp3(audio_file).duration_seconds
            clip_duration = audio_duration / num_clips

            for j in range(num_clips):
                start_index = j * max_lines_per_clip
                end_index = min((j + 1) * max_lines_per_clip, len(lines))
                clip_lines = lines[start_index:end_index]
                clip_text = "\n".join(clip_lines)

                text_clip = self._create_text_clip(clip_text, clip_duration, current_time, width, height)
                text_clips.append(text_clip)
                current_time += clip_duration

        return text_clips

    def _create_text_clip(self, text: str, duration: float, start: float, width: int, height: int):
        text_clip = TextClip(
            text,
            fontsize=65,
            color="white",
            size=(width, None),
            method="caption",
            font="Impact",
            stroke_color="black",
            stroke_width=4,
        )
        text_clip = text_clip.set_position("bottom").set_duration(duration).set_start(start)

        video_width, video_height = width, height
        text_width, text_height = text_clip.size
        scale_factor = min(video_width / text_width, video_height / text_height)
        new_width = int(text_width * scale_factor)
        new_height = int(text_height * scale_factor)

        # Folosim o funcție personalizată pentru redimensionare
        def resize_frame(frame):
            pil_image = Image.fromarray(frame)
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            return np.array(resized_image)

        text_clip = text_clip.fl_image(resize_frame)

        return text_clip
