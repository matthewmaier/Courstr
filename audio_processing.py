# audio_processing.py

import os
import subprocess
from pydub import AudioSegment

# Function to create an mp3 file using ffmpeg
def create_mp3_file(mp4_file):
    mp3_file = os.path.splitext(mp4_file)[0] + ".mp3"
    subprocess.run(["ffmpeg", "-i", mp4_file, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", mp3_file], check=True)  # Added check=True to raise an error if ffmpeg fails


# Function to split large MP3 files into chunks and create only missing chunks using PyDub
def split_large_mp3(mp3_file):
    max_size = 20 * 1024 * 1024  # Maximum size in bytes (20MB)
    file_size = os.path.getsize(mp3_file)
    
    if file_size > max_size:
        audio = AudioSegment.from_mp3(mp3_file)
        duration_per_chunk = int((max_size / file_size) * len(audio))
        chunks = int((len(audio) / duration_per_chunk) + 1)
        
        for i in range(chunks):
            start_time = i * duration_per_chunk
            chunk_file = mp3_file.replace(".mp3", f"-{start_time}.mp3")
            if not os.path.exists(chunk_file):
                print(f"Creating chunk {(i + 1)} of {chunks}")
                end_time = min((i + 1) * duration_per_chunk, len(audio))
                chunk_audio = audio[start_time:end_time]
                chunk_audio.export(chunk_file, format="mp3")
