import os
import subprocess
from glob import glob
from urllib.parse import urlparse

# Function to list all mp4 files for a given URL
def list_mp4_files(url):
    # Assuming the URL is a local file path to a directory containing MP4 files
    path = urlparse(url).path
    return glob(os.path.join(path, '*.mp4'))

# Function to check for matching MP3 files
def check_matching_mp3(mp4_files):
    missing_mp3_files = []
    for mp4_file in mp4_files:
        mp3_file = mp4_file.rsplit('.', 1)[0] + '.mp3'
        if not os.path.exists(mp3_file):
            missing_mp3_files.append(mp4_file)
    return missing_mp3_files

# Function to rip MP3 from MP4 using ffmpeg
def rip_mp3_from_mp4(mp4_file):
    mp3_file = mp4_file.rsplit('.', 1)[0] + '.mp3'
    subprocess.run(['ffmpeg', '-i', mp4_file, '-q:a', '0', '-map', 'a', mp3_file], check=True)
    print(f"Created new MP3 file: {mp3_file}")

# Main execution
if __name__ == "__main__":
    print("Beginning of main.py")

    tasks_dir = "tasks"
    for txt_file in glob(os.path.join(tasks_dir, '*.txt')):
        with open(txt_file, 'r') as file:
            urls = file.readlines()
        
        for url in urls:
            url = url.strip()
            mp4_files = list_mp4_files(url)
            missing_mp3_files = check_matching_mp3(mp4_files)
            
            for mp4_file in missing_mp3_files:
                print(f"Missing MP3 for: {mp4_file}")
                rip_mp3_from_mp4(mp4_file)

    print("End of main.py")
