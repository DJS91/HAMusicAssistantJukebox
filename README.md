# <img src="logo.png" width="25" height="25"> Music Assistant Jukebox Integration (Depricated)

## Notice: this integration is not longer activly being maintained.

Music Assistant now has a Plugin that should be used instead and offers much of the same features.
See https://beta.music-assistant.io/plugins/party-mode/

---

A Home Assistant integration that provides a web-based song request system that integrates with Music Assistant to create an interactive jukebox experience for guests!

![Jukebox Interface](showcase.avifs)

## Features
- Real-time song search across all connected Music Assistant providers
- Minimalist responsive design with album artwork display
- Check whats Now Playing and Up Next in real time.
- No login required for guests, just share the URL
- Queue management through Home Assistant entities
- Auto queues a default party playlist when the request queue is empty
- Control queuing frequency (limit queue spamming) 
- Access control through Home Assistant
- Auto revoking/creating access tokens for security

Head on over to [Discussions / FeatureRequests](https://github.com/DJS91/HAMusicAssistantJukebox/discussions) if you want to request new features and general discussion!

## Prerequisites

Before installing this integration, make sure you have:
- Home Assistant instance with [Music Assistant](https://github.com/music-assistant/hass-music-assistant) integration
- Music Assistant Server Addon in Home Assistant (Seperately hosted HA/MA instances may not work)
- A supported music provider configured in Music Assistant (e.g. Spotify, Apple Music, etc.)
- Media player entity configured in Home Assistant

## Installation

### HACS (Recommended)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=DJS91&repository=HAMusicAssistantJukebox&category=Integration)

or
1. Add this repository to HACS as a custom repository
   - HACS > Menu > Custom repositories
   - URL: `https://github.com/DJS91/HAMusicAssistantJukebox`
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

Access the jukebox via the new "Music Assistant Jukebox" Sidebar Panel OR

Scan the QR Code entity of choice OR 

Access the jukebox interface directly at:
```
http://homeassistant:8123/local/jukebox/jukebox.html
```

## Entities
The integration adds these entities to Home Assistant:

### Switches
- `switch.jukebox_queue`: Enable/disable queuing of songs (No manual control required. Managed by automation.)
- `switch.jukebox_allow_access`: Enable/disable access to the jukebox interface
- `switch.music_assistant_jukebox_jukebox_play_music_on_start`: Turn on/off if the default playlist plays automatically when the jukbox is turned on.
  
### Number
- `number.jukebox_queue_length`: Shows current queue length (No manual adjustment required, Managed by automation)
- `number.music_assistant_jukebox_jukebox_queuing_delay`: Set a delay between song requests for guests (seconds) (0 = off)
  
### Sensor
- `music_assistant_jukebox_external_qr_code`: External Jukebox UI Access QR code image for easy sharing on dashboards for users not on your network
- `music_assistant_jukebox_internal_qr_code`: Internal Jukebox UI Access QR code image for easy sharing for users on your network

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

## Credits
Big thanks to:
- [OddPirate](https://github.com/TheOddPirate) for their contrubutions to making this into an integration.

- [PilaScat](https://github.com/PilaScat) for their contributions to clean up, polish and UI improvements.

