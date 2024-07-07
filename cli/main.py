import click
from youtuber import VideoGenerator
import asyncio
import sys

@click.command()
@click.option('--prompt', required=True, help='Prompt for video generation')
@click.option('--length', default=1, type=int, help='Length of the video in minutes')
@click.option('--text-model', default='claude', help='Text model to use')
@click.option('--image-model', default='sd3', help='Image model to use')
@click.option('--verbose', is_flag=True, help='Enable verbose output')

def generate_video_cli(prompt, length, text_model, image_model, verbose):
    video_generator = VideoGenerator()

    async def run_with_progress():
        try:
            with click.progressbar(length=5, label='Generating video') as bar:
                subject = await video_generator.generate_and_upload(
                    prompt, length, text_model, image_model,
                    progress_callback=lambda stage: bar.update(1) if not verbose else None,
                    verbose=verbose
                )
            click.echo(f"\nVideo generated and uploaded for subject: {subject}")
        except Exception as e:
            click.echo(f"\nError occurred: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(run_with_progress())

if __name__ == '__main__':
    generate_video_cli()
