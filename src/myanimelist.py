import imp
import os
import glob
from pydoc import describe
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import requests
from dataclasses import dataclass


EXTENSION_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THUMBNAILS_DIR = EXTENSION_DIR + "/thumbnails/"

API_ENDPOINT = "https://api.myanimelist.net/v2"
ANIME_URL = "https://myanimelist.net/anime"
MANGA_URL = "https://myanimelist.net/manga"


@dataclass
class MyAnimeListEntry:
    icon: str
    name: str
    description: str
    on_enter: OpenUrlAction


def search(search_query, preferences, type="all"):
    api_key = preferences["api_key"]

    result_items = []

    animes = []
    mangas = []

    if type == "manga":
        mangas = list(
            search_query, API_ENDPOINT + "/manga", MANGA_URL, api_key, "manga", 10
        )
    elif type == "anime":
        animes = list(
            search_query, API_ENDPOINT + "/anime", ANIME_URL, api_key, "anime", 10
        )
    else:
        if preferences["search_anime"] == "true":
            animes = list(
                search_query, API_ENDPOINT + "/anime", ANIME_URL, api_key, "anime"
            )
        if preferences["search_manga"] == "true":
            mangas = list(
                search_query, API_ENDPOINT + "/manga", MANGA_URL, api_key, "manga"
            )

    all_items = animes + mangas

    for item in all_items:
        result_items.append(
            ExtensionResultItem(
                icon=item.icon,
                name=item.name,
                on_enter=item.on_enter,
                description=item.description,
            )
        )

    return result_items


def list(search_query, endpoint, site_url, api_key, type, limit=5):
    response = requests.get(
        endpoint,
        params={
            "q": search_query,
            "limit": limit,
            "fields": "start_date,rank,popularity,media_type",
        },
        headers={"X-MAL-Client-ID": api_key},
    )

    items = []

    for entry in response.json()["data"]:
        node = entry["node"]

        thumbnail_url = node["main_picture"]["medium"]

        name = node["title"]
        thumbnail_path = download_thumbnail(thumbnail_url, node["id"])

        start_date = node["start_date"]
        rank = node["rank"]
        popularity = node["popularity"]
        media_type = node["media_type"]

        description = "{} | started: {} | ranked: {} | popularity: {} | {}".format(
            type, start_date, rank, popularity, media_type
        )

        items.append(
            MyAnimeListEntry(
                icon=thumbnail_path,
                name=name,
                on_enter=OpenUrlAction(site_url + "/" + str(node["id"])),
                description=description,
            )
        )

    return items


def download_thumbnail(url, entry_id):
    if not os.path.exists(THUMBNAILS_DIR):
        os.makedirs(THUMBNAILS_DIR)

    thumbnail_path = THUMBNAILS_DIR + str(entry_id)
    file_content = requests.get(url)

    with open(thumbnail_path, "wb") as output_file:
        output_file.write(file_content.content)

    return thumbnail_path


def clear_thumbnails():
    files = glob.glob(THUMBNAILS_DIR + "*")

    for file in files:
        os.remove(file)
