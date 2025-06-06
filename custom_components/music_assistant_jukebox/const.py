"""Constants for music_assistant_jukebox."""

from logging import Logger, getLogger
import os
LOGGER: Logger = getLogger(__package__)

DOMAIN = "music_assistant_jukebox"
CONF_MUSIC_ASSISTANT_ID = "music_assistant_id"
CONF_MEDIA_PLAYER = "media_player"

# File paths
WWW_JUKEBOX_DIR = "www/jukebox"
TOKEN_FILE = f"{WWW_JUKEBOX_DIR}/jukeboxtoken.key"
HTML_FILE = f"{WWW_JUKEBOX_DIR}/jukebox.html"
MEDIA_FOLDER = f"{WWW_JUKEBOX_DIR}/media"
BLUEPRINT_FILE = "blueprints/automation/music_assistant_jukebox/jukebox_controller.yaml"