
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from tqdm import tqdm
from glob import glob
from datetime import datetime, timedelta
from file_utils import list_mp4_files, check_mp3_file, get_duration
from audio_processing import create_mp3_file
from transcription_services import check_transcript, create_transcript, check_subtitles, create_subtitles

# Load environment variables from .env file
load_dotenv()

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

