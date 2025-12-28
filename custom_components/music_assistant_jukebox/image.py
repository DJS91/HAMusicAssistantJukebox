"""Image platform for music_assistant_jukebox."""
from __future__ import annotations

import os
from datetime import datetime

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up image entities based on a config entry."""
    entities = [
        JukeboxInternalQRCode(hass, entry),
        JukeboxExternalQRCode(hass, entry),
    ]
    async_add_entities(entities)

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

class JukeboxQRBase(JukeboxBaseMixin, ImageEntity):
    """Base class for Jukebox QR codes to avoid duplication."""

    _attr_has_entity_name = True
    _attr_content_type = "image/png"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, name: str, unique_id: str, file_name: str) -> None:
        """Initialize the image entity."""
        super().__init__(hass)
        self.hass = hass
        self.entry = entry
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{unique_id}"
        self._image_path = hass.config.path(f"www/jukebox/{file_name}")
        self._attr_entity_picture = f"/local/jukebox/{file_name}"
        self._image: bytes | None = None

    async def async_image(self) -> bytes | None:
        """Return bytes of image by loading it via the executor."""
        return await self.hass.async_add_executor_job(self._load_image_sync)

    def _load_image_sync(self) -> bytes | None:
        """Load the image from disk (runs in executor)."""
        if not os.path.exists(self._image_path):
            self._attr_available = False
            return None

        try:
            self._attr_available = True
            self._attr_image_last_updated = datetime.fromtimestamp(os.path.getmtime(self._image_path))
            with open(self._image_path, "rb") as image_file:
                return image_file.read()
        except Exception as err:
            LOGGER.error("Error reading QR image %s: %s", self._image_path, err)
            self._attr_available = False
            return None

class JukeboxInternalQRCode(JukeboxQRBase):
    """Representation of the Jukebox Internal QR Code."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the internal QR entity."""
        super().__init__(
            hass, 
            entry, 
            "Internal Access QR Code", 
            "internal_qr", 
            "internal_url_qr.png"
        )

class JukeboxExternalQRCode(JukeboxQRBase):
    """Representation of the Jukebox External QR Code."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the external QR entity."""
        super().__init__(
            hass, 
            entry, 
            "External Access QR Code", 
            "external_qr", 
            "external_url_qr.png"
        )

