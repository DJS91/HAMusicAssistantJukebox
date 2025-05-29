# HAMusicAssistantJukebox

A web-based song request system that integrates with Home Assistant and Music Assistant to create an interactive jukebox experience for guests!

![alt text](https://github.com/DanStennett/HAMusicAssistantJukebox/blob/main/readme_image.jpg?raw=true)

https://github.com/user-attachments/assets/bea6223d-663b-40de-b3ec-5f62a9460696


## Features
- Real-time song search across all connected providers
- Minimalist responsive design with album artwork display
- No login, just share the URL/QR to guests and enjoy!
- Queue songs with your guests
- Auto queues a nominated default party playlist when jukebox requests are all played to keep the party going
- Access control through Home Assistant
- Auto revoking/creating access keys when enabling/disabling the service

## Prerequisites

- Home Assistant instance with Music Assistant integration
- A supported music provider configured in Music Assistant (e.g. Spotify, Apple Music)
- Media player entity configured in Home Assistant
- A default party playlist configured in MA for when the request queue is empty.

## Getting Started

### 1. Getting Required Values

 **Home Assistant URL** (`HAURL`):
   - Your Home Assistant instance URL (highly advise limiting this to your internal network only)
   - Example: `http://homeassistant.local:8123`

 **Music Assistant Config ID** (`MUSIC_ASSISTANT_CONFIG`):
   - In Home Assistant, go to Developer Tools > Actions
   - Find `music_assistant.search`
   - Select you Music Assistant Instance from the first dropdown.
   - Click on "GO TO YAML MODE"
   - Look for `config_entry_id` value in the service data
   - Copy the ID value

 **Media Player Entity** (`MEDIA_PLAYER`):
   - In Home Assistant, go to Developer Tools > States
   - Find your speaker's entity ID
   - Example: `media_player.party_speaker`

 **Webhook ID** (`QUEUEWEBHOOK`):
   - Required to let home assistant know which queuing type to choose
   - Create an automation with webhook trigger (See step 3 of Config & Setup)
   - Save the automation
   - Copy the webhook ID from the trigger

## 2. Configuration and Setup

Create these helpers in Home Assistant by adding this code to your configuration.yaml or creating them via the UI in Home Assistant Settings > Devices and Services > Helpers :

```yaml
input_boolean:
  songrequestaccess:
    name: Song Request Access
    initial: off
  jukebox_queue:
    name: Jukebox Queue Mode
    initial: off
input_number:
  jukebox_queue_length:
    name: Jukebox Queue Length
    initial: 0
    min: 0
    max: 100
```

1. **Set up API Token Management** 
   - Go to your Home Assistant Admin profile
   - Scroll to bottom under Long Lived Access Tokens
   - Click "Create Token" (this will be your management token and only used internally), name it JukeboxManagement.
   - Copy the generated token and paste it into the manage_token.py script in the parameter at the top of the script
   - Enter your HA local IP at the top of the script
   - Save the file
   - Copy the saved manage_token.py file to Config/python_scripts/manage_token.py (you can use the Samba Share or File Editor addons to access the HA folder structure)
   - open your Configuration.yaml and add these entries to your file:
     ```yaml
     shell_command:
        create_jukebox_token: python3 /config/python_scripts/manage_token.py 
        delete_jukebox_token: python3 /config/python_scripts/manage_token.py delete //revokes they key and deletes the key file from config/www
     ```
     The create_jukebox_token function generates a new token and puts it in a .key file in the config/www directory for use by the app.
     The delete_jukebox_token function deletes the token, revoking access and deletes the key file from the config/www directory.
   - Save your Configuration.yaml and restart home assistant.

2. **Set up the Disable/Enable Jukebox Automation**
   - Create a new home assistant automation using the Jukebox - Toggle Jukebox Access Access.yaml code
   - Save the automation

3. **Set up the Notify of Queued Song Automation**
   - Create a new home assistant automation using the Jukebox - Notify of Queued Song.yaml code
   - Replace the <YOUR WEBHOOK ID HERE> code with your own generated from the webhook trigger of the automation. (refer to the [HA documentation](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger) on how to set up webhooks) (example: [webhooks youtube vid](https://www.youtube.com/watch?v=2RP236gAPsM))
   - Save the automation
     
4. **Set up the set Default playlist when queue reaches zero Automation**
   - Create a new home assistant automation using the Jukebox - Set Default Playlist when Jukebox Queue is Zero.yaml code
   - Replace the <YOUR DEFAULT PARTY PLAYLIST HERE> with the name of your chosen default party playlist in music assistant.
   - Replace the <YOUR MEDIA PLAYER HERE> with the entity name of your chosen Music Assistant media player
   - Save the automation
     
5. **Set up the Track Queue Size Automation**
   - Create a new home assistant automation using the Jukebox - Track Queue Size.yaml code 
   - Replace the <YOUR MEDIA PLAYER HERE> with your chosen Music Assistant media player from the previous steps
   - Save the automation.


6. **HTML Configuration Values**

Update the configuration section in `jukebox.html`:

```javascript
const HAURL = 'http://[YOUR HA ADDRESS]:8123'; // Your internal HA URL
const QUEUEWEBHOOK = "[YOUR_WEBHOOK_ID]"; // required to coordinate Jukebox Queue mode.
const MEDIA_PLAYER = "[media_player.YOUR_SPEAKER]"; // Your speaker entity to play the tuuuuuuunes
const MUSIC_ASSISTANT_CONFIG = "[YOUR_MUSIC_ASSISTANT_CONFIG_ID]"; // Your MA config ID
```

7. Update your Configuration yaml with the following:
```yaml
http:
  cors_allowed_origins:
    - "http://localhost:5500"
    - "http://127.0.0.1:5500"
    - "null"
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
    - ::1
```
then **save** and restart HA.

9. **Publish the HTML**
   - Place the configured HTML file to your config\www folder in Home Assistant along with the bg.jpg

   - If you've done everything right, test the url by switching on the input_boolean.songrequestaccess input boolean toggle and visiting the page in your browser.
     It should be something like http://homeassistant.local:8123/local/jukebox.html and the interface should appear.

## Usage Control

- Toggle `input_boolean.songrequestaccess` to enable/disable the interface and revoke/create access token.

## Additional enhancements:
I stream my music to a couple of android tv's using Chomecast around the house with MA.

Using PiPup on an android tv, you can display the QR code as a Picture-In-Picture pop up over your MA music player and trigger 
it to appear using the songrequestaccess switch helper created earlier so guests can easily Scan the QR
Code from your TV(s) when the request systems is active.

Guide to set up PiPUp on android tv's is here:
https://community.home-assistant.io/t/a-short-guide-for-setting-up-tv-pip-notifications-with-pipup/537084

## Troubleshooting

If you encounter issues:

1. Check browser console for errors
2. Verify all configuration values are correct
3. Ensure Home Assistant is accessible
4. Confirm Music Assistant is properly configured
5. Verify the media player entity is available

## Relevant Support Materials

- Home Assistant: [Community Forums](https://community.home-assistant.io/)
- Music Assistant: [Documentation](https://music-assistant.github.io/)
- Issues with this app: Open an issue on the repository

## Buy me a Coffee :)
[![PayPal Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?business=XEYGDHYHSMANJ&no_recurring=0&currency_code=AUD)
