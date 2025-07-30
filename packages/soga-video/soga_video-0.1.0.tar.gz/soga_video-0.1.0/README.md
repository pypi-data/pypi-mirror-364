# SOGA Video

A CLI tool to create videos from text tasks using AI.

## Features

- Takes a text task and breaks it into 3 scenes
- Generates an image for each scene using ModelScope API
- Creates TTS narration for each scene using Edge TTS (Microsoft Edge Text-to-Speech)
- Combines images and audio into a complete video
- Outputs organized folder structure with all assets and final video

## Installation

1. Install `uv` if you haven't already:
   ```bash
   pip install uv
   ```

2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd soga-video
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

## Setup

1. Create a `.env` file in the project root with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MODELSCOPE_API_KEY=your_modelscope_api_key_here
   ```

2. Optionally configure the TTS voice in `.env`:
   ```env
   TTS_VOICE=zh-CN-XiaoxiaoNeural
   ```
   
   For a list of available voices, see: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts

## Usage

### Command Line Interface

```bash
# Basic usage
uv run soga_video "Explain quantum computing in simple terms"

# Specify output directory
uv run soga_video -o my_video "Create a story about a robot learning to paint"
```

### As a Python Module

```python
from soga_video.config import load_config
from soga_video.generator import VideoGenerator

# Load configuration
config = load_config()

# Check if API keys are set
if not config['openai_api_key'] or config['openai_api_key'] == 'your_openai_api_key_here':
    print("Please set your OpenAI API key in the .env file")
    exit(1)

if not config['modelscope_api_key'] or config['modelscope_api_key'] == 'your_modelscope_api_key_here':
    print("Please set your ModelScope API key in the .env file")
    exit(1)

# Create generator
generator = VideoGenerator(config)

# Create video
task = "Explain the process of photosynthesis in plants"
generator.create_video(task, "output_directory")
```

## Output Structure

The tool generates the following structure in the output directory:

```
output/
├── scene_1/
│   ├── image.png
│   ├── narration.mp3
│   └── scene.json
├── scene_2/
│   ├── image.png
│   ├── narration.mp3
│   └── scene.json
├── scene_3/
│   ├── image.png
│   ├── narration.mp3
│   └── scene.json
└── final_video.mp4
```

Each `scene.json` contains the prompt used for image generation and the text used for TTS. 
The final output is a complete video file `final_video.mp4` that combines all scenes.

## Development

To work on the project:

1. Install in development mode:
   ```bash
   uv sync --dev
   ```

2. Run tests:
   ```bash
   uv run pytest
   ```

3. Run example:
   ```bash
   uv run python example.py
   ```