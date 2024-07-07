import aiohttp
from aiohttp import FormData, MultipartWriter
import asyncio
import os
import base64
from typing import Literal
import json
from .config import Config
import openai

class ImageGenerator:
    def __init__(self, config: Config):
        self.config = config

    async def generate_images(self, subject: str, image_model: str, image_size: Literal["vertical", "horizontal"]):
        os.makedirs(f"./output/{subject}/images", exist_ok=True)
        with open(f"./output/{subject}/script.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            image_prompts = list(dict(data)["descriptions"])

        tasks = []
        for i, prompt in enumerate(image_prompts):
            if image_model == "dall-e-3":
                tasks.append(self._generate_image_dall_e(prompt, subject, image_size, i))
            elif image_model == "sd":
                tasks.append(self._generate_image_sd(prompt, subject, image_size, i))
            elif image_model == "sd3":
                tasks.append(self._generate_image_sd3(prompt, subject, image_size, i))

        await asyncio.gather(*tasks)

    async def _generate_image_dall_e(self, prompt: str, subject: str, image_size: str, iteration: int):
        if image_size == "vertical":
            size = "1024x1792"
        else:  # horizontal
            size = "1792x1024"

        client = openai.AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )

        if response.data and response.data[0].url:
            image_url = response.data[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    image_content = await resp.read()

            with open(f"./output/{subject}/images/{iteration+1}.png", "wb") as f:
                f.write(image_content)
        else:
            raise ValueError(f"Failed to generate image for prompt: {prompt}")


    async def _generate_image_sd3(self, prompt: str, subject: str, image_size: str, iteration: int):
        aspect_ratio = "9:16" if image_size == "vertical" else "16:9"

        # Creăm un obiect MultipartWriter
        mpwriter = MultipartWriter('form-data')

        # Adăugăm câmpurile necesare
        part = mpwriter.append(prompt)
        part.set_content_disposition('form-data', name='prompt')

        part = mpwriter.append('png')
        part.set_content_disposition('form-data', name='output_format')

        part = mpwriter.append(aspect_ratio)
        part.set_content_disposition('form-data', name='aspect_ratio')

        headers = {
            "Authorization": f"Bearer {self.config.SD_API_KEY}",
            "Accept": "image/*"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                headers=headers,
                data=mpwriter
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(f"./output/{subject}/images/{iteration+1}.png", "wb") as f:
                        f.write(content)
                else:
                    error_text = await response.text()
                    raise Exception(f"Error in SD3 image generation: {response.status} - {error_text}")
