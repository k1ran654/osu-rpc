import requests
import time
import os
from dotenv import load_dotenv
from pypresence import Presence

# === CONFIGURATION ===
load_dotenv()
OSU_CLIENT_ID = int(os.getenv("OSU_CLIENT_ID"))
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
OSU_USERNAME = input("Enter your username here: ")

modes = {
    "1": "osu",
    "2": "taiko",
    "3": "fruits",
    "4": "mania"
}
usr_choice = input("Enter the desired gamemode you would like to track!\n 1 = standard, 2 = taiko, 3 = catch, 4 = mania\n")

mode = modes.get(usr_choice, "osu")

display_logic = {}

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
    global mode
    url = f'https://osu.ppy.sh/api/v2/users/{OSU_USERNAME}/{mode}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()

def get_recent_beatmap(token, user_id):
    url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/recent?limit=1'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]['beatmap']['id']
    return None

def get_display_choice():
    global display_logic

    def prompt_multi(message, default_vals):
        user_input = input(message).strip()
        parts = user_input.split() if user_input else default_vals
        stat_a = parts[0] if len(parts) > 0 else default_vals[0]
        stat_b = parts[1] if len(parts) > 1 else default_vals[1]
        return stat_a, stat_b

    def prompt_single(message, default_val):
        return input(message).strip() or default_val


    stat1, stat2 = prompt_multi(
        "Select 2 stats for the top line! (1=Global Rank, 2=Country/Region Rank, 3=Performance Points)\n", 
        ["1", "3"]
    )
    stat3, stat4 = prompt_multi(
        "\nSelect 2 stats for the 2nd line! (1=Accuracy, 2=Total Plays, 3=Level, 4=Rank Change in the last 30 days)\n", 
        ["1", "4"]
    )
    stat5 = prompt_single(
        "\nSelect big image hover! (1=Playtime, 2=Total Score, 3=Ranked Score, 4=Max Combo)\n", 
        "1"
    )
    stat6 = prompt_single(
        "\nSelect small image hover! (1=Total Hits, 2=Country/Region Ranking)\n", 
        "1"
    )


    top_map = {
        "1": lambda s: f"Rank: #{s.get('global_rank', 0):,}",
        "2": lambda s: f"Country: #{s.get('country_rank', 0):,}",
        "3": lambda s: f"{s.get('pp', 0)}pp"
    }
    
    state_map = {
        "1": lambda s: f"Acc: {s.get('accuracy', 0)*100:.2f}%",
        "2": lambda s: f"Plays: {s.get('play_count', 0):,}",
        "3": lambda s: f"Lv. {s.get('level', {}).get('current', 0)}",
        "4": lambda s: f"Change: {s.get('rank_change_since_30_days', 0):+d}"
    }

    large_map = {
        "1": lambda s: f"Playtime: {s.get('play_time', 0) // 3600}h",
        "2": lambda s: f"Total Score: {s.get('total_score', 0):,}",
        "3": lambda s: f"Ranked Score: {s.get('ranked_score', 0):,}",
        "4": lambda s: f"Max Combo: {s.get('maximum_combo', 0):,}"
    }

    small_map = {
        "1": lambda s: f"Total Hits: {s.get('total_hits', 0):,}",
        "2": lambda s: f"Region Rank: #{s.get('country_rank', 0):,}"
    }

    display_logic = {
        "details": lambda s: f"{top_map.get(stat1, top_map['1'])(s)} | {top_map.get(stat2, top_map['3'])(s)}",
        "state": lambda s: f"{state_map.get(stat3, state_map['1'])(s)} | {state_map.get(stat4, state_map['2'])(s)}",
        "large": large_map.get(stat5, large_map['1']),
        "small": small_map.get(stat6, small_map['1'])
    }
# === MAIN LOOP ===

def main():
    get_display_choice()
    
    print("Connecting to Discord...")
    rpc = Presence(DISCORD_CLIENT_ID)
    rpc.connect()
    
    print("Script started! Press Ctrl+C to stop.")
    
    token = None
    while True:
        try:
            if not token:
                token = get_osu_token()
                
            user_data = get_osu_data(token)
            stats = user_data['statistics']
            user_id = user_data.get('id')
            
            rpc_buttons = [{"label": "View Profile", "url": f"https://osu.ppy.sh/users/{user_id}"}]
            
            recent_map_id = get_recent_beatmap(token, user_id)
            if recent_map_id:
                rpc_buttons.append({"label": "Recent Map", "url": f"https://osu.ppy.sh/beatmaps/{recent_map_id}"})
            
            rpc.update(
                details=display_logic["details"](stats),
                state=display_logic["state"](stats),
                large_image="osu",
                large_text=display_logic["large"](stats),
                small_image="pfp",
                small_text=display_logic["small"](stats),
                buttons=rpc_buttons
            )
            
            print(f"Status Updated: {time.strftime('%H:%M:%S')}")
            time.sleep(60)
            
        except Exception as e:
            print(f"Error occurred: {e}. Retrying in 30 seconds...")
            if "401" in str(e): token = None 
            time.sleep(30)

if __name__ == "__main__":
    main()