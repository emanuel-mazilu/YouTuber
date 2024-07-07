from fastapi import FastAPI
from pydantic import BaseModel
from youtuber import VideoGenerator

app = FastAPI()
video_generator = VideoGenerator()

class VideoRequest(BaseModel):
    prompt: str
    length: int
    text_model: str = "claude"
    image_model: str = "sd3"

@app.post("/generate_video")
async def generate_video_api(request: VideoRequest):
    subject = await video_generator.generate_and_upload(
        request.prompt,
        request.length,
        request.text_model,
        request.image_model
    )
    return {"status": "success", "subject": subject}
