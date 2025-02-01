import requests
import os
import time
from pathlib import Path

class PodcastConverter:
    def __init__(self):
        # Replace with your actual ElevenLabs API key
        self.api_key = "sk_5c3434cff70fb61b6615d31218ae3505f33a38d42fce6159"
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        # Voice IDs for Alex and Martin
        self.voice_ids = {
            "Alex": "ErXwobaYiN019PkySvjV",  # Adam voice
            "Martin": "VR6AewLTigWG4xSOukaG"  # Daniel voice
        }

    def convert_to_speech(self, text, speaker, output_filename):
        """Convert text to speech using ElevenLabs API"""
        url = f"{self.base_url}/text-to-speech/{self.voice_ids[speaker]}/stream"
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 200:
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                print(f"Created: {output_filename}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error converting text to speech: {str(e)}")
            return False

    def process_conversation(self, input_file):
        """Process the conversation file and generate audio files"""
        # Create output directory
        output_dir = Path("audio_output")
        output_dir.mkdir(exist_ok=True)

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_speaker = None
            current_text = []
            part = 1

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("Alex:") or line.startswith("Martin:"):
                    # Process previous speaker's text if exists
                    if current_speaker and current_text:
                        text = " ".join(current_text)
                        output_file = output_dir / f"{current_speaker.lower()}_part_{part}.mp3"
                        self.convert_to_speech(text, current_speaker, str(output_file))
                        part += 1
                        time.sleep(1)  # Avoid rate limiting

                    # Start new speaker
                    current_speaker = line.split(":")[0]
                    current_text = [line.split(":", 1)[1].strip()]
                else:
                    if current_speaker:
                        current_text.append(line)

            # Process the last part
            if current_speaker and current_text:
                text = " ".join(current_text)
                output_file = output_dir / f"{current_speaker.lower()}_part_{part}.mp3"
                self.convert_to_speech(text, current_speaker, str(output_file))

        except FileNotFoundError:
            print(f"Error: Could not find input file {input_file}")
        except Exception as e:
            print(f"Error processing conversation: {str(e)}")

def main():
    # File paths
    input_file = "final1.txt"  # Make sure this file exists in your directory
    # Create converter instance
    converter = PodcastConverter()

    # Process the conversation
    print("Starting conversion...")
    converter.process_conversation(input_file)
    print("Conversion completed!")

if __name__ == "__main__":
    main()