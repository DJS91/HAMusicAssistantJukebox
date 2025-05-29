"""The Music Assistant Jukebox integration."""
from __future__ import annotations

import os
import aiofiles
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import (
    DOMAIN,
    LOGGER,
    WWW_JUKEBOX_DIR,
    HTML_FILE,
    BLUEPRINT_FILE,
    CONF_MEDIA_PLAYER,
    CONF_MUSIC_ASSISTANT_ID,
    BG_FILE
)
PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Music Assistant Jukebox from a config entry."""
    
    # Initialize the data store
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    try:
        # Create jukebox directory in www if it doesn't exist
        www_path = Path(hass.config.path(WWW_JUKEBOX_DIR))
        www_path.mkdir(parents=True, exist_ok=True)

        # Get component directory path
        component_path = Path(__file__).parent

        # Copy files from www directory
        original_path = Path(__file__).parent / "files"
        
        # Define files to copy including blueprint
        files_to_copy = {
            "bg.jpg": BG_FILE
            "jukebox.html": HTML_FILE,
            "jukebox_controller.yaml": BLUEPRINT_FILE
        }

        for src_name, dst_path in files_to_copy.items():
            src_file = original_path / src_name
            dst_file = Path(hass.config.path(dst_path))
            
            # Ensure parent directory exists
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                LOGGER.info("Copied %s to %s", src_name, dst_file)
            else:
                LOGGER.error("Source file %s not found", src_file)

        # Update jukebox.html with correct values
        html_file = Path(hass.config.path(HTML_FILE))
        if html_file.exists():
            async with aiofiles.open(html_file, mode='r') as file:
                content = await file.read()

            # Get URL - try internal first, then external
            internal_url = hass.config.internal_url
            external_url = hass.config.external_url
            # This method does not work setting it to default hostname for now
            base_url = "homeassistant.local"#internal_url or external_url

            if not base_url:
                # Fallback to core config base_url
                if hasattr(hass.config, 'api') and hass.config.api.base_url:
                    base_url = hass.config.api.base_url
                else:
                    LOGGER.error("No internal or external URL configured in Home Assistant")
                    return False

            # Remove trailing slash
            base_url = base_url.rstrip("/")
            
            # Replace placeholder values
            replacements = {
                "your_music_assistant_config_id": entry.data[CONF_MUSIC_ASSISTANT_ID],
                "media_player.your_speaker": entry.data[CONF_MEDIA_PLAYER],
                "<your HA IP here>": base_url
            }

            for old, new in replacements.items():
                if new is None:
                    LOGGER.error("Missing replacement value for %s", old)
                    return False
                content = content.replace(old, str(new))

            # Write updated content back
            async with aiofiles.open(html_file, mode='w') as file:
                await file.write(content)
            
            LOGGER.info("Updated jukebox.html with: %s", replacements)

    except Exception as err:
        LOGGER.error("Error setting up files: %s", err)
        return False

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        try:
            # Clean up files
            www_path = Path(hass.config.path(WWW_JUKEBOX_DIR))
            if www_path.exists():
                shutil.rmtree(www_path)
                LOGGER.info("Removed jukebox files from www directory")
            blueprint_path = Path(hass.config.path("blueprints/automation/music_assistant_jukebox/"))
            if blueprint_path.exists():
                shutil.rmtree(blueprint_path)
                LOGGER.info("Removed Blueprint files")
            refresh_tokens = hass.auth._store.async_get_refresh_tokens()
            # Remove existing tokens for jukeboxmanagement
            for token in refresh_tokens:
                if token.client_name == "jukeboxmanagement":
                    hass.auth._store.async_remove_refresh_token(token)
                    LOGGER.debug("Removed existing jukebox token")

        except Exception as err:
            LOGGER.error("Error during cleanup: %s", err)
        
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
