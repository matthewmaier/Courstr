import os
import subprocess
from glob import glob
from urllib.parse import urlparse

# Function to list all mp4 files for a given URL
def list_mp4_files(url):
    try:
        # Assuming the URL is a local file path to a directory containing MP4 files
        path = urlparse(url).path
        return glob(os.path.join(path, '*.mp4'))
    except Exception as e:
        print(f"Error listing MP4 files: {e}")
        return []

# Function to check for matching MP3 files
def check_matching_mp3(mp4_files):
    missing_mp3_files = []
    for mp4_file in mp4_files:
        try:
            mp3_file = mp4_file.rsplit('.', 1)[0] + '.mp3'
            if not os.path.exists(mp3_file):
                missing_mp3_files.append(mp4_file)
        except Exception as e:
            print(f"Error checking for MP3 file: {e}")
    return missing_mp3_files

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
                missing_mp3_files = check_matching_mp3(mp4_files)
                
                for mp4_file in missing_mp3_files:
                    print(f"Missing MP3 for: {mp4_file}")
                    rip_mp3_from_mp4(mp4_file)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")

    print("End of main.py")
