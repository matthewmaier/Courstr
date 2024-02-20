"""
This one I started from scratch in https://aitools.favtutor.com/
I used the 5 free message credits to reproduce everything Cursor wrote
But it had a better structure (probably better prompting from me)
Then I improve this with Cursor's AI and a little manual editing
"""

import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from urllib.parse import urlparse
from glob import glob
import webvtt
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Function to list mp4 files in a folder
def list_mp4_files(folder):
    mp4_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".mp4"):  # Ensure case-insensitive comparison
                mp4_files.append(os.path.join(root, file))
    return mp4_files

# Function to check if an mp3 file exists for a given mp4 file
def check_mp3_file(mp4_file):
    mp3_file = os.path.splitext(mp4_file)[0] + ".mp3"
    return os.path.exists(mp3_file)

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

# Function to check if an English transcript exists for a given mp3 file
def check_transcript(mp3_file):
    transcript_file = os.path.splitext(mp3_file)[0] + "-en.txt"
    return os.path.exists(transcript_file)

# Function to create an English transcript using OpenAI API
def create_transcript(mp3_file, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    
    try:
        # Check if the MP3 file needs to be split into chunks
        if os.path.getsize(mp3_file) > 20 * 1024 * 1024:
            split_large_mp3(mp3_file)
            transcript_text = ""
            chunk_files = sorted(glob(mp3_file.replace(".mp3", "-*.mp3")))
            for chunk in chunk_files:
                transcript_chunk_file = chunk.replace(".mp3", "-en.txt")
                if not os.path.exists(transcript_chunk_file):
                    with open(chunk, "rb") as audio:
                        response = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio,
                            response_format="text"
                        )
                        if isinstance(response, dict) and "text" in response:
                            transcript_text += response["text"]
                        else:
                            transcript_text += str(response)
                    with open(transcript_chunk_file, "w") as f:
                        f.write(transcript_text)
            # Combine all transcript chunks into one file
            with open(os.path.splitext(mp3_file)[0] + "-en.txt", "w") as combined_transcript:
                for chunk_file in chunk_files:
                    transcript_chunk_file = chunk_file.replace(".mp3", "-en.txt")
                    with open(transcript_chunk_file, "r") as f:
                        combined_transcript.write(f.read())
        else:
            transcript_file = os.path.splitext(mp3_file)[0] + "-en.txt"
            if not os.path.exists(transcript_file):
                with open(mp3_file, "rb") as audio:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        response_format="text"
                    )
                    if isinstance(response, dict) and "text" in response:
                        transcript_text = response["text"]
                    else:
                        transcript_text = str(response)
                    with open(transcript_file, "w") as f:
                        f.write(transcript_text)
    except Exception as e:
        print(f"Error creating transcript for {mp3_file}: {str(e)}")
        print(f"END error creating transcript for {mp3_file}")

# Function to check if English subtitles exist for a given mp3 file
def check_subtitles(mp3_file):
    subtitles_file = os.path.splitext(mp3_file)[0] + "-en.vtt"
    return os.path.exists(subtitles_file)

# Function to create English subtitles using OpenAI API
def create_subtitles(mp3_file, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    
    def adjust_time(timestamp, seconds):
        t = datetime.strptime(timestamp, "%H:%M:%S.%f")
        d = timedelta(seconds=seconds)
        new_timestamp = t + d
        return new_timestamp.strftime("%H:%M:%S.%f")

    try:
        # Check if the MP3 file needs to be split into chunks
        if os.path.getsize(mp3_file) > 20 * 1024 * 1024:
            split_large_mp3(mp3_file)
            chunk_files = sorted(glob(mp3_file.replace(".mp3", "-*.mp3")))
            for chunk in chunk_files:
                start_time_str = chunk.split("-")[-1].replace(".mp3", "")
                start_time_seconds = int(start_time_str) / 1000  # Convert from milliseconds to seconds
                subtitles_file = chunk.replace(".mp3", "-en.vtt")
                if not os.path.exists(subtitles_file):
                    with open(chunk, "rb") as audio:
                        response = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio,
                            response_format="vtt"
                        )
                        if isinstance(response, dict) and "content" in response:
                            with open(subtitles_file, "w") as f:
                                f.write(response["content"])
                        else:
                            with open(subtitles_file, "w") as f:
                                f.write(str(response))
                    vtt = webvtt.read(subtitles_file)
                    for caption in vtt.captions:
                        caption.start = adjust_time(caption.start, start_time_seconds)
                        caption.end = adjust_time(caption.end, start_time_seconds)
                    vtt.save(subtitles_file)
                    # Check if the subtitles file is empty and print an error if it is
                    if os.path.getsize(subtitles_file) == 0:
                        print(f"Error: Subtitles file {subtitles_file} is empty.")
            # Combine all subtitle chunks into one file
            with open(os.path.splitext(mp3_file)[0] + "-en.vtt", "w") as combined_subtitles:
                for chunk_file in chunk_files:
                    subtitles_chunk_file = chunk_file.replace(".mp3", "-en.vtt")
                    with open(subtitles_chunk_file, "r") as f:
                        combined_subtitles.write(f.read())
        else:
            subtitles_file = os.path.splitext(mp3_file)[0] + "-en.vtt"
            if not os.path.exists(subtitles_file):
                with open(mp3_file, "rb") as audio:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        response_format="vtt"
                    )
                    if isinstance(response, dict) and "content" in response:
                        with open(subtitles_file, "w") as f:
                            f.write(response["content"])
                    else:
                        with open(subtitles_file, "w") as f:
                            f.write(str(response))
                vtt = webvtt.read(subtitles_file)
                for caption in vtt.captions:
                    caption.start = adjust_time(caption.start, 0)
                    caption.end = adjust_time(caption.end, 0)
                vtt.save(subtitles_file)
                # Check if the subtitles file is empty and print an error if it is
                if os.path.getsize(subtitles_file) == 0:
                    print(f"Error: Subtitles file {subtitles_file} is empty.")
    except Exception as e:
        print(f"Error creating subtitles for {mp3_file}: {str(e)}")
        print(f"END Error creating subtitles for {mp3_file}")

# Main function
def main():
    tasks_folder = "tasks"  # Replace with the path to your tasks folder

    openai_api_key = os.getenv("OPENAI_API_KEY")

    print("Starting script...")
    
    # Read URLs from text files in the tasks folder
    for text_file in glob(os.path.join(tasks_folder, '*.txt')):
        try:
            with open(text_file, 'r') as file:
                urls = file.readlines()
                
            for url in urls:
                url = url.strip()
                folder_path = urlparse(url).path
                mp4_files = list_mp4_files(folder_path)
                
                for mp4_file in mp4_files:
                    try:
                        print(f"Processing file: {mp4_file}")
                        
                        if not check_mp3_file(mp4_file):
                            create_mp3_file(mp4_file)
                        
                        mp3_file = os.path.splitext(mp4_file)[0] + ".mp3"
                        
                        if not check_transcript(mp3_file):
                            create_transcript(mp3_file, openai_api_key)
                        
                        if not check_subtitles(mp3_file):
                            create_subtitles(mp3_file, openai_api_key)
                    
                    except Exception as e:
                        print(f"Error processing file: {mp4_file}: {str(e)}")
                        print(f"END error in mp4_file try")
        except Exception as e:
            print(f"Error reading {text_file}: {str(e)}")
            print(f"END error in text_file try")

    print("Script completed.")

if __name__ == "__main__":
    main()

