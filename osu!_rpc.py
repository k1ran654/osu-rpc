import requests
import time
import os
from dotenv import load_dotenv
from pypresence import Presence

# === CONFIGURATION ===
load_dotenv()
OSU_CLIENT_ID = int(os.getenv("OSU_CLIENT_ID"))
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
OSU_USERNAME = os.getenv("OSU_USERNAME")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")

# === FUNCTIONS ===

def get_osu_token():
    url = 'https://osu.ppy.sh/oauth/token'
    data = {
        'client_id': OSU_CLIENT_ID,
        'client_secret': OSU_CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    response = requests.post(url, data=data)
    return response.json().get('access_token')

def get_osu_data(token):
    url = f'https://osu.ppy.sh/api/v2/users/{OSU_USERNAME}/osu'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()

# === MAIN LOOP ===

def main():
    print("Connecting to Discord...")
    rpc = Presence(DISCORD_CLIENT_ID)
    rpc.connect()
    
    print("Script started! Press Ctrl+C to stop.")
    
    while True:
        try:
            token = get_osu_token()
            user_data = get_osu_data(token)
            
            stats = user_data['statistics']
            rank = stats['global_rank']
            pp = stats['pp']
            acc = round(stats['hit_accuracy'], 2)
            
            rpc.update(
                state=f"Rank: #{rank:,} | {pp}pp",
                details=f"Accuracy: {acc}%",
                large_image="osu_logo",
                large_text=f"Total Playtime: {stats['play_time'] // 3600} hours"
            )
            
            print(f"Status Updated: #{rank} - {pp}pp")
            
            time.sleep(60)
            
        except Exception as e:
            print(f"Error occurred: {e}. Retrying in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    main()