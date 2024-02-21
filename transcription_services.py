# transcription_services.py

import os
from glob import glob
from openai import OpenAI
import webvtt
from datetime import datetime, timedelta
from audio_processing import split_large_mp3

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
                            transcript_text = response["text"]
                        else:
                            transcript_text = str(response)
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