import click
import os
from soga_video.generator import VideoGenerator
from soga_video.config import load_config

@click.command()
@click.argument('task', type=click.STRING)
@click.option('--output-dir', '-o', default='output', help='Output directory for generated videos')
def main(task, output_dir):
    """Create a video from a text task"""
    config = load_config()

    print("=== config ====")
    print(config)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    generator = VideoGenerator(config)
    generator.create_video(task, output_dir)

if __name__ == '__main__':
    main()