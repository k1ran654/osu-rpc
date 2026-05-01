# OSU-RPC
osu-rpc is a script that runs in the background and provides a customizable osu! Rich Presence on Discord.

## How does it work?
It fetches real-time player statistics via the osu! API v2 and displays them on your Discord profile using the `pypresence` library.

## Features
- **Customizable Stats:** You can choose which statistics to display on the top and bottom lines during setup.
- **Game Mode Support:** Track Standard, Taiko, Catch, or Mania.
- **Interactive Buttons:** Direct links to your profile and your most recent beatmap.
- **Hover Info:** Dedicated slots for playtime, total score, and region rankings.

## Setup
1. **Requirements:**
   ```bash
   pip install requests python-dotenv pypresence
   ```
2. **Configuration:**
   Create a `.env` file with the following:
   ```env
   OSU_CLIENT_ID=your_id
   OSU_CLIENT_SECRET=your_secret
   DISCORD_CLIENT_ID=your_discord_id
   ```
3. **Discord Assets:**
   In your Discord Developer Portal, upload two Rich Presence assets named exactly:
   - `osu` (Large image)
   - `pfp` (Small image)

## How to use it
Run the script and follow the prompts:
```bash
python osu!_rpc.py
```
*Note: When choosing two stats, enter the numbers separated by a space (e.g., `1 3`).*

## Troubleshooting
- **DNS/NameResolutionError:** Usually a temporary internet issue. The script will automatically retry every 30 seconds.
- **Images:** If images don't appear, double-check that your asset names in the Discord Portal are exactly "osu" and "pfp".
