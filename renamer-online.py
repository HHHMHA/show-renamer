import glob
import os
import re
from typing import Dict

import requests

show_name = input("Enter show name (eg: The Boys): ")
print(f"Searching for {show_name}...")

response = requests.get('http://api.tvmaze.com/singlesearch/shows', params={'q': show_name})

if response.status_code == 404:
    print("Sorry no shows matches the name, please refine your search")
    exit(-1)

show = response.json()
print("Success!")
print(f"Fond show {show['name']} with id {show['id']}")

# Try Downloading Cover Image
if input("Do you want to download cover? (N for no any other key to download): ").upper() != "N":
    try:
        print("Trying to download cover...")
        image_url = show["image"]["original"]
        image_extension = image_url[-3:]
        image_response = requests.get(image_url)
        file = open(f"cover.{image_extension}", "wb")
        file.write(image_response.content)
        file.close()
        print("Successfully downloaded cover")
    except:
        print("Unable to download cover, either you don't have write permissions or no image exists.")

season_number = int(input("Enter season number (eg: 1): "))
show_episodes = requests.get(f'http://api.tvmaze.com/shows/{show["id"]}/episodes').json()

video_extension = input("Enter video file extension (eg: mkv): ")
subtitle_extension = input("Enter subtitle file extension (eg: srt): ")

episode_files = glob.glob(f'*.{video_extension}')
subtitle_files = glob.glob(f'*.{subtitle_extension}')

if input("Waining files will be renamed in order of their names (lexical order). press N to exit").upper() == 'N':
    exit(0)


def get_subtitle(episode: str) -> str:
    for subtitle_path in subtitle_files:
        if subtitle_path.upper().find(episode) > -1:
            return subtitle_path


def get_episode_meta(episode_number: int) -> Dict:
    for episode_meta in show_episodes:
        if episode_meta['season'] == season_number and episode_meta['number'] == episode_number:
            return episode_meta
    return {}


for episode_file in episode_files:
    episode = re.findall(r'[Ee]\d\d', episode_file)[0].upper()
    subtitle = get_subtitle(episode)

    episode_meta = get_episode_meta(int(episode[1:]))
    new_name_no_extension = f'E{episode_meta["number"]:02d} {episode_meta["name"]}'

    if subtitle is not None and input(f"Rename {subtitle} to {new_name_no_extension}? Press N to cancel it: ").upper() != "N":
        new_subtitle_name = new_name_no_extension + f'.{subtitle_extension}'
        os.rename(subtitle, new_subtitle_name)
    if input(f"Rename {episode_file} to {new_name_no_extension}? Press N to cancel it: ").upper() != "N":
        new_name = new_name_no_extension + f'.{video_extension}'
        os.rename(episode_file, new_name)

input("Press any key to exit")
