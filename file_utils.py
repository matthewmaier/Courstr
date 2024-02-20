# file_utils.py

import os
from urllib.parse import urlparse

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

# Function to get the duration of an mp4 file using ffprobe
def get_duration(filename):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        duration = float(result.stdout)
        return duration
    except Exception as e:
        print(f"Error getting duration of file {filename}: {e}")
        return None
