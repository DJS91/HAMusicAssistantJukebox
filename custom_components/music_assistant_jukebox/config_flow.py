"""Adds config flow for Blueprint."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.core import callback

from .const import DOMAIN, LOGGER, CONF_MUSIC_ASSISTANT_ID, CONF_MEDIA_PLAYER


class JukeboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""

        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        try:
            if user_input is not None:
                # Validate the input
                entity_registry = er.async_get(self.hass)
                media_player_entry = entity_registry.async_get(user_input[CONF_MEDIA_PLAYER])

                if not media_player_entry:
                    errors["base"] = "invalid_media_player"
                else:
                    # Check if Music Assistant integration exists
                    ma_entries = self.hass.config_entries.async_entries("music_assistant")
                    if not ma_entries:
                        errors["base"] = "no_music_assistant"
                    else:
                        return self.async_create_entry(
                            title="Music Assistant Jukebox",
                            data={
                                CONF_MEDIA_PLAYER: user_input[CONF_MEDIA_PLAYER],
                                CONF_MUSIC_ASSISTANT_ID: user_input[CONF_MUSIC_ASSISTANT_ID],
                            },
                        )

            # Get list of media players from Music Assistant
            entity_registry = er.async_get(self.hass)
            ma_media_players = {
                entity_id: entity
                for entity_id, entity in entity_registry.entities.items()
                if (entity.domain == MEDIA_PLAYER_DOMAIN and 
                    entity.platform == "music_assistant")
            }

            # Get Music Assistant config entries
            ma_entries = self.hass.config_entries.async_entries("music_assistant")

            if not ma_media_players:
                errors["base"] = "no_music_assistant_players"
            elif not ma_entries:
                errors["base"] = "no_music_assistant"
            else:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_MEDIA_PLAYER): vol.In(
                                {
                                    entity_id: entity.name or entity_id
                                    for entity_id, entity in ma_media_players.items()
                                }
                            ),
                            vol.Required(CONF_MUSIC_ASSISTANT_ID): vol.In(
                                {entry.entry_id: entry.title for entry in ma_entries}
                            ),
                        }
                    ),
                    errors=errors,
                )

        except Exception as error:
            LOGGER.exception("Unexpected error: %s", error)
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )
