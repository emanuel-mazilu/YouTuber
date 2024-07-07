from .config import Config
from .script_generator import ScriptGenerator
from .image_generator import ImageGenerator
from .audio_generator import AudioGenerator
from .video_creator import VideoCreator
from .uploader import YouTubeUploader
import asyncio

class VideoGenerator:
    def __init__(self):
        self.config = Config()
        self.script_generator = ScriptGenerator(self.config)
        self.image_generator = ImageGenerator(self.config)
        self.audio_generator = AudioGenerator(self.config)
        self.video_creator = VideoCreator(self.config)
        self.uploader = YouTubeUploader(self.config)

    async def generate_and_upload(self, prompt: str, length: int, text_model: str, image_model: str, progress_callback=None, verbose=False):
        try:
            if verbose:
                print("Generating script...")
            subject = await self.script_generator.generate_script(prompt, length, text_model)
            if verbose:
                print(f"Script generated: {subject}")
            if progress_callback:
                progress_callback("script")

            # Creăm task-uri pentru generarea de imagini și audio
            image_task = asyncio.create_task(
                self.image_generator.generate_images(subject, image_model, "vertical" if length <= 1 else "horizontal")
            )
            audio_task = asyncio.create_task(
                self.audio_generator.generate_audio_files(subject, length)
            )

            # Așteptăm ca ambele task-uri să se termine
            if verbose:
                print("Generating images and audio in parallel...")
            await asyncio.gather(image_task, audio_task)
            if verbose:
                print("Images and audio generated.")
            if progress_callback:
                progress_callback("images_and_audio")

            if verbose:
                print("Creating video...")
            await self.video_creator.generate_video(subject, length)
            if verbose:
                print("Video created.")
            if progress_callback:
                progress_callback("video")

            if verbose:
                print("Uploading to YouTube...")
            await self.uploader.upload_to_youtube(subject)
            if verbose:
                print("Upload complete.")
            if progress_callback:
                progress_callback("upload")

            return subject
        except Exception as e:
            if verbose:
                print(f"An error occurred: {e}")
            raise
