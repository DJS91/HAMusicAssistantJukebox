"""The Music Assistant Jukebox integration."""
from __future__ import annotations

import os
import aiofiles
import shutil
import qrcode
from pathlib import Path
from homeassistant.helpers import network

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
    CONF_MUSIC_ASSISTANT_ID
)
PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.NUMBER, Platform.IMAGE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Music Assistant Jukebox from a config entry."""
    
    # Initialize the data store
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    try:
        # Create jukebox directory in www if it doesn't exist
        www_path = Path(hass.config.path(WWW_JUKEBOX_DIR))
        www_path.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Created/verified www directory at: %s", www_path)

        try:
            internal_url = str(network.get_url(hass, allow_internal=True, allow_external=False))
            external_url = str(network.get_url(hass, allow_internal=False, allow_external=True))
        
            # Append jukebox path
            internal_url = f"{internal_url}/local/jukebox/jukebox.html"
            external_url = f"{external_url}/local/jukebox/jukebox.html"
            
            LOGGER.info("URLs determined using network helpers - Internal: %s, External: %s", 
                        internal_url, external_url)
            
        except Exception as err:
            LOGGER.warning("Could not get URLs using network helpers: %s", err)
            # Fallback to default URL
            default_url = "http://homeassistant.local:8123/local/jukebox/jukebox.html"
            internal_url = default_url
            external_url = default_url
            LOGGER.info("Using fallback URLs: %s", default_url)

        LOGGER.info("URLs found - Internal: %s, External: %s", internal_url, external_url)

        if internal_url:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=2,
                )
                qr.add_data(internal_url)
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                qr_path = www_path / "internal_url_qr.png"
                LOGGER.info("Saving internal QR code to: %s", qr_path)
                qr_image.save(str(qr_path))  # Convert Path to string
                LOGGER.info("Created QR code for internal URL: %s", internal_url)
            except Exception as err:
                LOGGER.error("Error creating internal URL QR code: %s", err)

        if external_url:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=2,
                )
                qr.add_data(external_url)
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                qr_path = www_path / "external_url_qr.png"
                LOGGER.info("Saving external QR code to: %s", qr_path)
                qr_image.save(str(qr_path))  # Convert Path to string
                LOGGER.info("Created QR code for external URL: %s", external_url)
            except Exception as err:
                LOGGER.error("Error creating external URL QR code: %s", err)
        
        # Get component directory path
        component_path = Path(__file__).parent

        # Copy files from www directory
        original_path = Path(__file__).parent / "files"
        
        # Define files to copy including blueprint
        files_to_copy = {
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

        # Copy media folder if it exists
        media_src = original_path / "media"
        media_dst = www_path / "media"
        if media_src.exists() and media_src.is_dir():
            if media_dst.exists():
                shutil.rmtree(media_dst)
            shutil.copytree(media_src, media_dst)
            LOGGER.info("Copied media folder to %s", media_dst)

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
    
    # Register panel AFTER everything else is set up
    await async_register_panel(hass, entry)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    # Remove the panel first
    await async_remove_panel(hass)
    
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
        
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_register_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register the sidebar panel."""
    try:

        # Method 1: Try direct panel registration
        try:
            from homeassistant.components.frontend import async_register_built_in_panel
            
            # Register as a built-in panel
            async_register_built_in_panel(
                hass,
                component_name="iframe",
                sidebar_title="Music Assistant Jukebox",
                sidebar_icon="mdi:music",
                frontend_url_path="music_assistant_jukebox",
                config={"url": "/local/jukebox/jukebox.html"},
                require_admin=False,
            )
            LOGGER.info("Successfully registered panel using built-in method")
            return
            
        except Exception as err:
            LOGGER.warning("Built-in panel registration failed: %s", err)
        
        # Method 2: Try service call as fallback
        if "panel_iframe" in hass.config.components:
            await hass.services.async_call(
                "panel_iframe",
                "register",
                {
                    "frontend_url_path": "music_assistant_jukebox",
                    "sidebar_title": "Music Assistant Jukebox",
                    "sidebar_icon": "mdi:music",
                    "url": "/local/jukebox/jukebox.html",
                    "require_admin": False,
                },
                blocking=True,
            )
            LOGGER.info("Successfully registered panel using service call")
        else:
            LOGGER.error("panel_iframe component not available")
            
    except Exception as err:
        LOGGER.error("Failed to register panel: %s", err)


async def async_remove_panel(hass: HomeAssistant) -> None:
    """Remove the sidebar panel."""
    try:
        # Try to remove the panel
        from homeassistant.components.frontend import async_remove_panel
        
        async_remove_panel(hass, "music_assistant_jukebox")
        LOGGER.info("Successfully removed panel")
        
    except Exception as err:
        LOGGER.warning("Failed to remove panel: %s", err)
    """Register the sidebar panel."""
    try:
        # Check if panel_iframe is available
        if "panel_iframe" in hass.config.components:
            # Register using service call
            await hass.services.async_call(
                "panel_iframe",
                "register",
                {
                    "frontend_url_path": "music_assistant_jukebox",
                    "sidebar_title": "Music Assistant Jukebox",
                    "sidebar_icon": "mdi:music",
                    "url": "/local/jukebox/jukebox.html",
                    "require_admin": False,
                },
                blocking=True,
            )
            LOGGER.info("Successfully registered panel for %s", DOMAIN)
        else:
            LOGGER.error("panel_iframe component not available")
    except Exception as err:
        LOGGER.error("Failed to register panel: %s", err)
