"""The Music Assistant Jukebox integration."""
from __future__ import annotations

import os
import shutil
import logging
from pathlib import Path

import aiofiles
import qrcode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import network

from .const import (
    BLUEPRINT_FILE,
    CONF_MEDIA_PLAYER,
    CONF_MUSIC_ASSISTANT_ID,
    DOMAIN,
    HTML_FILE,
    LOGGER,
    WWW_JUKEBOX_DIR,
)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.NUMBER, Platform.IMAGE]

async def async_register_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register the sidebar panel."""
    try:
        # Use the frontend's async_register_built_in_panel
        # This is more reliable than a service call
        from homeassistant.components.frontend import async_register_built_in_panel
        
        async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title="Music Assistant Jukebox",
            sidebar_icon="mdi:music",
            frontend_url_path="music_assistant_jukebox",
            config={"url": "/local/jukebox/jukebox.html"},
            require_admin=False,
        )
        LOGGER.info("Successfully registered sidebar panel via frontend API")
            
    except Exception as err:
        LOGGER.error("Failed to register panel: %s", err)

async def async_remove_panel(hass: HomeAssistant) -> None:
    """Remove the sidebar panel."""
    try:
        from homeassistant.components.frontend import async_remove_panel as frontend_remove_panel
        frontend_remove_panel(hass, "music_assistant_jukebox")
        LOGGER.info("Successfully removed sidebar panel")
    except Exception as err:
        LOGGER.warning("Failed to remove panel (it may have already been removed): %s", err)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Music Assistant Jukebox from a config entry."""
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    try:
        www_path = Path(hass.config.path(WWW_JUKEBOX_DIR))
        
        # Determine URLs for QR Codes
        try:
            internal_url = str(network.get_url(hass, allow_internal=True, allow_external=False))
            external_url = str(network.get_url(hass, allow_internal=False, allow_external=True))
            internal_url = f"{internal_url}/local/jukebox/jukebox.html"
            external_url = f"{external_url}/local/jukebox/jukebox.html"
        except Exception as err:
            LOGGER.warning("Could not get URLs using network helpers: %s", err)
            default_url = "http://homeassistant.local:8123/local/jukebox/jukebox.html"
            internal_url = external_url = default_url

        # Define the blocking disk operations
        def perform_sync_setup():
            """Handle all blocking I/O (Filesystem and QR generation) in a thread."""
            # 1. Ensure directory exists
            www_path.mkdir(parents=True, exist_ok=True)

            # 2. Generate and save QR Codes
            for url, filename in [(internal_url, "internal_url_qr.png"), (external_url, "external_url_qr.png")]:
                if url:
                    qr = qrcode.QRCode(version=1, border=2, box_size=10)
                    qr.add_data(url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img.save(str(www_path / filename))

            # 3. Copy base files (HTML and Blueprint)
            original_path = Path(__file__).parent / "files"
            files_to_copy = {"jukebox.html": HTML_FILE, "jukebox_controller.yaml": BLUEPRINT_FILE}
            
            for src_name, dst_rel_path in files_to_copy.items():
                src_file = original_path / src_name
                dst_file = Path(hass.config.path(dst_rel_path))
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)

            # 4. Copy Media Folder
            media_src = original_path / "media"
            media_dst = www_path / "media"
            if media_src.exists() and media_src.is_dir():
                if media_dst.exists():
                    shutil.rmtree(media_dst)
                shutil.copytree(media_src, media_dst)

        # Run the blocking logic in the executor pool
        await hass.async_add_executor_job(perform_sync_setup)

        # 5. Update jukebox.html (Asynchronous content update)
        html_file = Path(hass.config.path(HTML_FILE))
        if html_file.exists():
            async with aiofiles.open(html_file, mode='r') as file:
                content = await file.read()

            base_url = "homeassistant.local"  # Static fallback as per your requirement
            replacements = {
                "your_music_assistant_config_id": entry.data[CONF_MUSIC_ASSISTANT_ID],
                "media_player.your_speaker": entry.data[CONF_MEDIA_PLAYER],
                "<your HA IP here>": base_url
            }

            for old, new in replacements.items():
                content = content.replace(old, str(new or ""))

            async with aiofiles.open(html_file, mode='w') as file:
                await file.write(content)

    except Exception as err:
        LOGGER.error("Error during file setup: %s", err)
        return False

    # Forward setup to platforms (switch, number, image)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register the sidebar panel
    await async_register_panel(hass, entry)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the sidebar panel
    await async_remove_panel(hass)
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        def cleanup_files():
            """Perform blocking file deletions."""
            www_path = Path(hass.config.path(WWW_JUKEBOX_DIR))
            if www_path.exists():
                shutil.rmtree(www_path)
            
            # Use the directory containing the blueprint for cleanup
            blueprint_dir = Path(hass.config.path("blueprints/automation/music_assistant_jukebox/"))
            if blueprint_dir.exists():
                shutil.rmtree(blueprint_dir)

        # Run cleanup in executor
        await hass.async_add_executor_job(cleanup_files)
        
        # Cleanup Refresh Tokens
        refresh_tokens = list(hass.auth._store.async_get_refresh_tokens())
        for token in refresh_tokens:
            if token.client_name == "jukeboxmanagement":
                hass.auth._store.async_remove_refresh_token(token)

        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

