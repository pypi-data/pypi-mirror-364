import os
import json
import asyncio
from typing import Dict, List, Any
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import edge_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

class VideoGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = OpenAI(api_key=config['openai_api_key'])
        
    def _generate_scenes(self, task: str) -> List[Dict[str, str]]:
        """Generate 3 scenes based on the task"""
        prompt = f"""
        Based on the following task, break it down into exactly 3 scenes for a video.
        Each scene should have:
        1. A visual description for image generation (1-2 sentences)
        2. A narration text (2-3 sentences)
        
        Task: {task}
        
        Respond ONLY in the following JSON format:
        {{
            "scenes": [
                {{
                    "image_prompt": "Description for image generation",
                    "narration": "Text for voiceover"
                }},
                {{
                    "image_prompt": "Description for image generation",
                    "narration": "Text for voiceover"
                }},
                {{
                    "image_prompt": "Description for image generation",
                    "narration": "Text for voiceover"
                }}
            ]
        }}
        """
        
        try:
            model = self.config['openai_model']
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result['scenes']
        except Exception as e:
            print(f"Warning: Failed to generate scenes with AI: {e}")
            # Fallback in case the model doesn't return valid JSON
            scenes = []
            for i in range(3):
                scenes.append({
                    "image_prompt": f"Visual representation for scene {i+1} of task: {task}",
                    "narration": f"This is the narration for scene {i+1} based on the task: {task}"
                })
            return scenes
    
    def _generate_image(self, prompt: str) -> bytes:
        """Generate an image using ModelScope API"""
        try:
            url = 'https://api-inference.modelscope.cn/v1/images/generations'
            
            payload = {
                'model': 'MusePublic/489_ckpt_FLUX_1',
                'prompt': prompt
            }
            headers = {
                'Authorization': f"Bearer {self.config['modelscope_api_key']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                url, 
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                headers=headers
            )
            
            response_data = response.json()
            image_url = response_data['images'][0]['url']
            image_response = requests.get(image_url)
            return image_response.content
        except Exception as e:
            print(f"Warning: Failed to generate image: {e}")
            raise e
    
    async def _generate_tts(self, text: str, output_path: str):
        """Generate TTS audio using edge-tts"""
        try:
            # Use default voice if not specified in config
            voice = self.config.get('tts_voice', 'zh-CN-XiaoxiaoNeural')
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
        except Exception as e:
            print(f"Warning: Failed to generate TTS: {e}")
            raise e
    
    def _create_video_from_scenes(self, scenes_dir: str, output_path: str):
        """Create a video from the generated scenes"""
        try:
            clips = []
            
            # Process each scene
            for i in range(1, 4):  # 3 scenes
                scene_dir = os.path.join(scenes_dir, f"scene_{i}")
                
                # Check if scene directory exists
                if not os.path.exists(scene_dir):
                    print(f"Warning: Scene {i} directory not found")
                    continue
                
                # Get image and audio paths
                image_path = os.path.join(scene_dir, "image.png")
                audio_path = os.path.join(scene_dir, "narration.mp3")
                
                # Check if files exist
                if not os.path.exists(image_path):
                    print(f"Warning: Image for scene {i} not found")
                    continue
                    
                if not os.path.exists(audio_path):
                    print(f"Warning: Audio for scene {i} not found")
                    continue
                
                # Create clip
                audio_clip = AudioFileClip(audio_path)
                image_clip = ImageClip(image_path).with_duration(audio_clip.duration)
                clip = image_clip.with_audio(audio_clip)
                clips.append(clip)
            
            # Concatenate clips
            if clips:
                final_clip = concatenate_videoclips(clips, method="compose")
                final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
                print(f"Video created successfully: {output_path}")
            else:
                print("Error: No valid clips to create video")
        except Exception as e:
            print(f"Warning: Failed to create video: {e}")
            raise e
    
    def create_video(self, task: str, output_dir: str):
        """Main method to create video from task"""
        print(f"Generating video for task: {task}")
        
        # Generate scenes
        scenes = self._generate_scenes(task)
        
        # Process each scene
        for i, scene in enumerate(scenes):
            print(f"Processing scene {i+1}/3...")
            
            # Create scene directory
            scene_dir = os.path.join(output_dir, f"scene_{i+1}")
            os.makedirs(scene_dir, exist_ok=True)
            
            # Save scene data
            with open(os.path.join(scene_dir, "scene.json"), "w") as f:
                json.dump(scene, f, indent=2)
            
            # Generate image
            try:
                image_data = self._generate_image(scene['image_prompt'])
                image_path = os.path.join(scene_dir, "image.png")
                with open(image_path, "wb") as f:
                    f.write(image_data)
                print(f"  - Generated image: {image_path}")
            except Exception as e:
                print(f"  - Error generating image: {e}")
                # Create a placeholder image
                self._create_placeholder_image(os.path.join(scene_dir, "image.png"))
            
            # Generate TTS
            try:
                tts_path = os.path.join(scene_dir, "narration.mp3")
                # Run the async function in a synchronous context
                asyncio.run(self._generate_tts(scene['narration'], tts_path))
                print(f"  - Generated audio: {tts_path}")
            except Exception as e:
                print(f"  - Error generating audio: {e}")
        
        # Create final video
        video_path = os.path.join(output_dir, "final_video.mp4")
        print("Creating final video...")
        self._create_video_from_scenes(output_dir, video_path)
        
        print(f"Video creation completed. Output saved to: {output_dir}")
    
    def _create_placeholder_image(self, path: str):
        """Create a placeholder image when generation fails"""
        img = Image.new('RGB', (1024, 1024), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Placeholder Image", fill=(255, 255, 0))
        img.save(path)