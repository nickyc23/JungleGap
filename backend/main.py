import os
import requests
from dotenv import load_dotenv


# Loads .env file
load_dotenv()


# Grabs API key from .env file
RIOT_API_KEY = os.getenv("RIOT_API_KEY")


# If API key is not correct, returns error message
if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY not found, check the backend/.env file.")


def get_puuid_by_riot_id(game_name, tag_line):
    """
    This function takes a Riot ID and splits it into two parts:
    - game_name: name before #
    - tag_line: the tag after the #


    Example:
    Riot ID: Big Boy Night#NA1
    game_name = "Big Boy Night"
    tag_line = "NA1" 
    """
    
    # Region variable since a regional routing endpoint is used
    region = "americas"


    # Building a Riot API link with selected region, player's game name, and their tagline
    url = (
        f"https://{region}.api.riotgames.com" 
        f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"  
    )

    # Creates request header that sends API key to Riot
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    # Sends GET request to the Riot API using URL and API key header
    response = requests.get(url, headers=headers)


    # Prints respone code to see if request worked
    print("Status Code:", response.status_code)

    # If Riot doesn't return a successful response, print error and stop function
    if response.status_code != 200:
        print("Error response:")
        print(response.text)
        return None
    
    # Convert Riot's JSON response to a python dictionary
    data = response.json()

    # Return just player PUUID from response data
    return data["puuid"]


def get_match_ids_by_puuid(puuid, count=5):
    """
    This functions uses a player's PUUID to get their recent match IDs.

    -puuid: player's unique Riot acc ID
    -count: how many recent matches requested
    """

    # Region variable since Match-V5 uses regional routing endpoints
    region = "americas"

    # Builds Riot API URL to get recent match IDs by PUUID
    url = (
        f"https://{region}.api.riotgames.com"
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        f"?start=0&count={count}"
    )

    # Request headers to send API key to Riot
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    # GET request to Riot's Match API
    response = requests.get(url, headers=headers)

    # Print status code to see if request worked
    print("Match IDs Status Code:", response.status_code)

    # If successful response isn't returned, print error and function ends
    if response.status_code != 200:
        print("Error response:")
        print(response.text)
        return None
    
    # Convert JSON to list
    data = response.json()

    # Return match IDs
    return data

def get_match_details(match_id):
    """
    Uses match ID to get full match details.

    Example:
    match_id = "NA1_12345768"

    Returns JSON with game info
    """

    # Build Riot API URL to get match details
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"

    # Request headers to sen API key to Riot
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    # Send GET request to Riot Match API 
    response = requests.get(url, headers=headers)

    # If requests fails, show error message and stop program
    if response.status_code != 200:
        raise Exception(f"Error getting match details: {response.status_code}, {response.text}")
    
    return response.json()

def find_player_in_match(match_data, puuid):
    """
    This function looks for the searched player in the match.

    Match data has all 10 players, so player PUUID is used to find exact participant.
    """

    participants = match_data["info"]["participants"]

    for player in participants:
        if player["puuid"] == puuid:
            return player
        
    return None

def extract_jungle_stats(player):
    """
    Takes player's match data and get stats for JungleGap.

    Transforms Riot's large data dictionary into a smaller, cleaner version with just important jungle stats.
    """

    time_played_minutes = player["timePlayed"] / 60


    stats = {
        "champion": player["championName"],
        "role": player["teamPosition"],
        "win": player["win"],

        "kills": player["kills"],
        "deaths": player["deaths"],
        "assists": player["assists"],

        "gold_earned": player["goldEarned"],
        "gold_per_min": round(player["goldEarned"] / time_played_minutes, 2),

        "neutral_minions_killed": player["neutralMinionsKilled"],
        "jungle_cs_per_min": round(player["neutralMinionsKilled"] / time_played_minutes, 2),

        "vision_score": player["visionScore"],
        "vision_score_per_min": round(player["visionScore"] / time_played_minutes, 2),

        "damage_to_champions": player["totalDamageDealtToChampions"],
        "damage_per_min": round(player["totalDamageDealtToChampions"] / time_played_minutes, 2),

        "dragon_kills": player["dragonKills"],
        "baron_kills": player["baronKills"],
        "objectives_stolen": player["objectivesStolen"],

        "time_played_minutes": time_played_minutes
    }

    return stats

# Ran if only the file is ran directly
if __name__ == "__main__":

    # Asks user to enter the Riot name before the #
    game_name = input("Enter your Riot name: ").strip()

    # Asks user to enter tagline after #
    tag_line = input("Enter tagline without #: ").strip()

    # Calls function and stores returned PUUID
    puuid = get_puuid_by_riot_id(game_name, tag_line)

    # If there is a PUUID, print to terminal
    if puuid: 
        print("PUUID found:")
        print(puuid)

        match_ids = get_match_ids_by_puuid(puuid, count=5)

        if match_ids:
            print("Recent Match IDS:")
            for match_id in match_ids:
                print(match_id)

            first_match_id = match_ids[0]

            match_data = get_match_details(first_match_id)

            player = find_player_in_match(match_data, puuid)

            if player:
                print("Player found in match.")

                jungle_stats = extract_jungle_stats(player)

                print("Jungle Stats:")
                for stat_name, stat_value in jungle_stats.items():
                    print(stat_name, ":", stat_value)
            else:
                print("Player not found in this match.")
        else:
            print("No match IDs found.")
    else: 
        print("No PUUID found.")

