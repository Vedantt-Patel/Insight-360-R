from pydub import AudioSegment
import os
from pathlib import Path
import re

class PodcastCombiner:
    def __init__(self, input_dir="audio_output"):
        self.input_dir = Path(input_dir)
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Directory {input_dir} not found")

    def get_sorted_audio_files(self):
        """Get audio files sorted by part number"""
        files = []
        for file in self.input_dir.glob("*.mp3"):
            match = re.search(r'part_(\d+)', file.name)
            if match:
                part_num = int(match.group(1))
                files.append((part_num, file))

        return [file for _, file in sorted(files)]

    def combine_audio(self, output_file="final_podcast.mp3"):
        """Combine all audio files into one podcast"""
        try:
            print("Starting audio combination process...")

            audio_files = self.get_sorted_audio_files()
            if not audio_files:
                raise Exception("No MP3 files found in the input directory")
            print(f"Processing: {audio_files[0].name}")
            combined = AudioSegment.from_mp3(str(audio_files[0]))
            pause = AudioSegment.silent(duration=500)

            for audio_file in audio_files[1:]:
                print(f"Processing: {audio_file.name}")
                segment = AudioSegment.from_mp3(str(audio_file))
                combined += pause + segment

            output_path = self.input_dir / output_file
            print(f"\nExporting combined podcast to: {output_path}")
            combined.export(str(output_path), format="mp3")
            print("Podcast combination completed successfully!")

            # Print duration
            duration_sec = len(combined) / 1000
            minutes = int(duration_sec // 60)
            seconds = int(duration_sec % 60)
            print(f"Final podcast duration: {minutes}m {seconds}s")
            self.delete_audio_files(audio_files)

        except Exception as e:
            print(f"Error combining audio files: {str(e)}")
            raise

    def delete_audio_files(self, audio_files):
        """Delete all individual audio files after merging"""
        print("\nDeleting individual audio files...")
        for file in audio_files:
            try:
                file.unlink()  
                print(f"Deleted: {file.name}")
            except Exception as e:
                print(f"Failed to delete {file.name}: {str(e)}")

def main():
    try:
        combiner = PodcastCombiner()
        combiner.combine_audio()

    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nPlease ensure:")
        print("1. The audio_output directory exists and contains MP3 files")
        print("2. The files are named correctly (e.g., alex_part_1.mp3)")
        print("3. You have write permissions in the output directory")

if __name__ == "__main__":
    main()
