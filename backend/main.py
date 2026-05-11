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