# Started this file from scratch using Cursor's built-in AI coder
# This approach ended up struggling to deliver the transcriptions

import os
import subprocess
from openai import OpenAI
from glob import glob
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load the OpenAI API key from the .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Function to list all mp4 files for a given URL
def list_mp4_files(url):
    try:
        # Assuming the URL is a local file path to a directory containing MP4 files
        path = urlparse(url).path
        return glob(os.path.join(path, '*.mp4'))
    except Exception as e:
        print(f"Error listing MP4 files: {e}")
        return []

# Function to check for matching MP3 files and transcripts
def check_media_files(mp4_files):
    missing_files = {'mp3': [], 'transcript': [], 'subtitles': []}
    for mp4_file in mp4_files:
        try:
            base_filename = mp4_file.rsplit('.', 1)[0]
            mp3_file = base_filename + '.mp3'
            transcript_file = base_filename + '-en.txt'
            subtitles_file = base_filename + '-en.vtt'

            if not os.path.exists(mp3_file):
                missing_files['mp3'].append(mp4_file)
            if not os.path.exists(transcript_file):
                missing_files['transcript'].append(mp3_file)
            if not os.path.exists(subtitles_file):
                missing_files['subtitles'].append(mp3_file)
        except Exception as e:
            print(f"Error checking media files for {mp4_file}: {e}")
    return missing_files

# Function to rip MP3 from MP4 using ffmpeg
def rip_mp3_from_mp4(mp4_file):
    try:
        mp3_file = mp4_file.rsplit('.', 1)[0] + '.mp3'
        subprocess.run(['ffmpeg', '-i', mp4_file, '-q:a', '0', '-map', 'a', mp3_file], check=True)
        print(f"Created new MP3 file: {mp3_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {mp4_file} to MP3: {e}")
    except Exception as e:
        print(f"Unexpected error during conversion: {e}")

# Function to create transcript and subtitles using OpenAI's API
def create_transcript_and_subtitles(mp3_file):
    try:
        base_filename = mp3_file.rsplit('.', 1)[0]
        transcript_file = base_filename + '-en.txt'
        subtitles_file = base_filename + '-en.vtt'

        # Open the MP3 file
        with open(mp3_file, 'rb') as audio_file:
            # Use OpenAI's API to create the transcript
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="text",
                language="en"
            )

            # Use OpenAI's API to create the subtitles
            subtitles_response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="vtt",
                language="en"
            )

        # Save the transcript
        with open(transcript_file, 'w') as f:
            f.write(transcript_response['text'])

        # Save the subtitles
        with open(subtitles_file, 'w') as f:
            f.write(subtitles_response['text'])

        print(f"Created new transcript: {transcript_file}")
        print(f"Created new subtitles: {subtitles_file}")
    except Exception as e:
        print(f"Error creating transcript or subtitles for {mp3_file}: {e}")

# Main execution
if __name__ == "__main__":
    print("Beginning of main.py")

    tasks_dir = "tasks"
    for txt_file in glob(os.path.join(tasks_dir, '*.txt')):
        try:
            with open(txt_file, 'r') as file:
                urls = file.readlines()
        except FileNotFoundError:
            print(f"File not found: {txt_file}")
            continue
        except Exception as e:
            print(f"Error reading {txt_file}: {e}")
            continue
        
        for url in urls:
            try:
                url = url.strip()
                mp4_files = list_mp4_files(url)
                missing_files = check_media_files(mp4_files)
                
                for mp4_file in missing_files['mp3']:
                    print(f"Missing MP3 for: {mp4_file}")
                    rip_mp3_from_mp4(mp4_file)
                
                for mp3_file in missing_files['transcript']:
                    print(f"Missing transcript for: {mp3_file}")
                    create_transcript_and_subtitles(mp3_file)
                
                for mp3_file in missing_files['subtitles']:
                    print(f"Missing subtitles for: {mp3_file}")
                    # Subtitles will be created along with the transcript in the same function call
                    # No need to call the function again if transcript is also missing
                    if mp3_file not in missing_files['transcript']:
                        create_transcript_and_subtitles(mp3_file)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")

    print("End of main.py")
