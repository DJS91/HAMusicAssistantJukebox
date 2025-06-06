# Music Assistant Jukebox Integration

A Home Assistant integration that provides a web-based song request system that integrates with Music Assistant to create an interactive jukebox experience for guests!

![Jukebox Interface](https://github.com/DanStennett/HAMusicAssistantJukebox/blob/main/readme_image.jpg?raw=true)

## Features
- Real-time song search across all connected Music Assistant providers
- Minimalist responsive design with album artwork display
- No login required for guests, just share the URL
- Queue management through Home Assistant entities
- Auto queues a default party playlist when the request queue is empty
- Access control through Home Assistant
- Auto revoking/creating access tokens for security

## Prerequisites

Before installing this integration, make sure you have:
- Home Assistant instance with [Music Assistant](https://github.com/music-assistant/hass-music-assistant) integration
- A supported music provider configured in Music Assistant (e.g. Spotify, Apple Music, etc.)
- Media player entity configured in Home Assistant

## Installation

### HACS (Recommended)
1. Add this repository to HACS as a custom repository
   - HACS > Menu > Custom repositories
   - URL: `https://github.com/DJS91/music-assistant-jukebox`
   - Category: Integration
2. Click Install
3. Restart Home Assistant

### Manual Installation
1. Download the latest release
2. Copy the `custom_components/music_assistant_jukebox` folder to your Home Assistant `custom_components` folder
3. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Music Assistant Jukebox"
4. Select your Music Assistant instance and media player entity
5. Go to Settings > Automations & Scenes > + Create Automation
6. Select "Music Assistant Jukebox Controller" from the list.
7. Enter the same media player entity from Step 4 and enter the name of your default playlist from music assistant and click Save.

## Usage
Switch on the jukebox using "JukeBox: Allow access" switch.
Access the jukebox interface at:
```
http://homeassistant:8123/local/jukebox/jukebox.html
```

## Entities
The integration adds these entities to Home Assistant:

### Switches
- `switch.jukebox_queue`: Enable/disable queuing of songs (No manual control required. Managed by automation.)
- `switch.jukebox_allow_access`: Enable/disable access to the jukebox interface

### Number
- `number.jukebox_queue_length`: Shows current queue length (No manual adjustment required, Managed by automation)


## Automation Blueprint

The integration includes an automation blueprint that handles:
- Queue length tracking
- Default playlist fallback
- Access control
- Media player control

To use the blueprint:
1. Go to Settings > Automations & Scenes
2. Click "+ Create Automation"
3. Select "Music Assistant Jukebox Controller"
4. Configure:
   - Media Player: Select your Music Assistant media player
   - Default Playlist: Enter the name of your fallback playlist

## Contributing

Feel free to contribute! Open an issue or submit a PR.

## Credits

Based on the original [HAMusicAssistantJukebox](https://github.com/DJS91/HAMusicAssistantJukebox) by DJS91.
Integration developed by @DJS91 and @TheOddPirate.

