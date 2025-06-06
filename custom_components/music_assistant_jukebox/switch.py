"""Switch platform for music_assistant_jukebox."""
from __future__ import annotations

import os
from pathlib import Path
import secrets
import string
from typing import Any

from datetime import timedelta
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.auth.const import GROUP_ID_ADMIN
from homeassistant.auth.models import User

from .const import (
    DOMAIN,
    LOGGER,
    WWW_JUKEBOX_DIR,
    TOKEN_FILE,
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches based on a config entry."""
    switches = [
        JukeboxQueueSwitch(hass, entry),
        JukeboxAccessSwitch(hass, entry),
    ]
    async_add_entities(switches)

class JukeboxBaseMixin:
    """Mixin for common device info."""
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "jukebox")},
            name="Music Assistant Jukebox",
            manufacturer="DJS91 and TheOddPirate",
            model="Jukebox Controller",
            configuration_url="http://homeassistant.local:8123/local/jukebox/jukebox.html"
        )

class JukeboxQueueSwitch(JukeboxBaseMixin, SwitchEntity):
    """Representation of the Jukebox Queue switch."""
    
    _attr_has_entity_name = True
    _attr_name = "JukeBox: queue"
    _attr_unique_id = "jukebox_queue"
    _attr_icon = "mdi:playlist-music"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self.hass = hass
        self.entry = entry
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on queue."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off queue."""
        self._attr_is_on = False
        self.async_write_ha_state()

class JukeboxAccessSwitch(JukeboxBaseMixin, SwitchEntity):
    """Representation of the Jukebox Access switch."""

    _attr_has_entity_name = True
    _attr_name = "JukeBox: Allow access"
    _attr_unique_id = "songrequestaccess"
    _attr_icon = "mdi:key"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self.hass = hass
        self.entry = entry
        self._attr_is_on = False
        self._token = entry.data.get("access_token")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on access and generate token."""
        try:
            #if not self._token:
            user = await self.hass.auth.async_get_owner()
            
            # Get all refresh tokens through the auth store
            refresh_tokens = self.hass.auth._store.async_get_refresh_tokens()
            # Remove existing tokens for jukeboxmanagement
            for token in refresh_tokens:
                if token.client_name == "jukeboxmanagement":
                    self.hass.auth._store.async_remove_refresh_token(token)
                    LOGGER.debug("Removed existing jukebox token")

            # Create a refresh token first
            refresh_token = await self.hass.auth.async_create_refresh_token(
                user,
                client_name="jukeboxmanagement",
                client_icon="mdi:music-box",
                token_type="long_lived_access_token",
                access_token_expiration=timedelta(days=1)
            )
            
            # Create an access token from the refresh token
            self._token = self.hass.auth.async_create_access_token(refresh_token)
            
            LOGGER.debug("Created new access token: %s", self._token[:50] + "...")
            
            # Store token in config entry
            new_data = dict(self.entry.data)
            new_data["access_token"] = self._token
            self.hass.config_entries.async_update_entry(
                self.entry,
                data=new_data
            )
            LOGGER.debug("Stored new token in config entry")
            #else:
                #LOGGER.debug("Using existing token: %s", self._token[:50] + "...")
        
            # Create token file regardless if token is new or existing
            token_dir = Path(self.hass.config.path(WWW_JUKEBOX_DIR))
            token_dir.mkdir(parents=True, exist_ok=True)
            
            token_path = Path(self.hass.config.path(TOKEN_FILE))
            token_path.write_text(self._token)
            
            self._attr_is_on = True
            self.async_write_ha_state()
            LOGGER.info("Access token file created successfully")
            
        except Exception as err:
            LOGGER.error("Failed to create access token file: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off access and remove token file."""
        try:
            # Get all refresh tokens through the auth store
            refresh_tokens = self.hass.auth._store.async_get_refresh_tokens()
            
            # Remove existing tokens for jukeboxmanagement
            for token in refresh_tokens:
                if token.client_name == "jukeboxmanagement":
                    self.hass.auth._store.async_remove_refresh_token(token)
                    LOGGER.debug("Removed existing jukebox token")
            
            # Just remove the token file
            token_path = Path(self.hass.config.path(TOKEN_FILE))
            if token_path.exists():
                token_path.unlink()
            
            self._attr_is_on = False
            self.async_write_ha_state()
            LOGGER.info("Access token file removed successfully")
            
        except Exception as err:
            LOGGER.error("Failed to remove access token file: %s", err)
