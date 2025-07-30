import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..libs.anilist.types import AnilistDateObject, AnilistMediaNextAiringEpisode

COMMA_REGEX = re.compile(r"([0-9]{3})(?=\d)")


# TODO: Add formating options for the final date
def format_anilist_date_object(anilist_date_object: "AnilistDateObject"):
    if anilist_date_object and anilist_date_object["day"]:
        return f"{anilist_date_object['day']}/{anilist_date_object['month']}/{anilist_date_object['year']}"
    else:
        return "Unknown"


def format_anilist_timestamp(anilist_timestamp: int | None):
    if anilist_timestamp:
        return datetime.fromtimestamp(anilist_timestamp).strftime("%d/%m/%Y %H:%M:%S")
    else:
        return "Unknown"


def format_list_data_with_comma(data: list | None):
    if data:
        return ", ".join(data)
    else:
        return "None"


def format_number_with_commas(number: int | None):
    if not number:
        return "0"
    return COMMA_REGEX.sub(lambda match: f"{match.group(1)},", str(number)[::-1])[::-1]


def extract_next_airing_episode(airing_episode: "AnilistMediaNextAiringEpisode"):
    if airing_episode:
        return f"{airing_episode['episode']} on {format_anilist_timestamp(airing_episode['airingAt'])}"
    else:
        return "Completed"
