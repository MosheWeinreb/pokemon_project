import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict, Any


# Function to get URLs of Pokémon pages
def get_pokemon_urls(URL: str) -> List[str]:
    response = requests.get( URL )  # Send GET request
    response.raise_for_status()  # Check if request was successful
    soup = BeautifulSoup( response.content, 'html.parser' )  # Parse webpage content
    # Find links to individual Pokémon pages and construct full URLs
    pokemon_urls = ['https://pokemondb.net' + a['href'] for a in soup.select( '.infocard a.ent-name' )][
                   :10]  # change amount of files if needed
    return pokemon_urls


# Function to extract  height or weight from Pokémon's webpage
def extract_measure(soup: BeautifulSoup, measure_name: str) -> float:
    # Find the measure (height/weight) element, extract and convert numeric value
    measure = float( soup.find( 'table', class_='vitals-table' ).find( 'th', string=measure_name ).find_next_sibling(
        'td' ).text.strip().split()[0] )
    return measure


def evolutin_check(soup: BeautifulSoup, pokemon_url):
    try:
        evolution_elements = soup.select( '.infocard a.ent-name' )
        evolution_urls = ['https://pokemondb.net' + a['href'] for a in evolution_elements]
        if evolution_urls[-1] != pokemon_url:
            for index, evolution_url in enumerate( evolution_urls ):
                if evolution_url != pokemon_url:
                    return evolution_urls[index + 1]
    except:
        return ("none")

    # Function to scrape details of each Pokémon


def scrape_pokemon_details(pokemon_url: str) -> Dict[str, Any]:
    response = requests.get( pokemon_url )  # Send GET request

    soup = BeautifulSoup( response.content, 'html.parser' )  # Parse webpage content
    # Extract various details: ID, name, types, height, weight, abilities, evolution URL
    original_id = soup.find( 'table', class_='vitals-table' ).find( 'strong' ).text.strip()
    id_ = int( original_id )
    name = soup.find( 'h1' ).text
    types = f"[{', '.join( [a.text for a in soup.find( 'table', class_='vitals-table' ).find_all( 'a', class_='type-icon' )] )}]"  # join for it to be on the same line
    height = extract_measure( soup, "Height" )  # Extract height
    weight = extract_measure( soup, "Weight" )  # Extract weight
    abilities = f"[{', '.join( [a.text for a in soup.find( 'th', string='Abilities' ).find_next_sibling( 'td' ).find_all( 'a' )] )}]"  # join for it to be on the same line
    evolutin_url = evolutin_check( soup, pokemon_url )

    # dict of the data except original id that is for json key (I feel like there is another way)
    pokemon_data = {
        "id": id_,
        "name": name,
        "types": types,
        "height": height,
        "weight": weight,
        "abilities": abilities,
        "evolution": evolutin_url
    }
    return original_id, pokemon_data


# Main code execution
def main():
    main_page_URL: str = 'https://pokemondb.net/pokedex/national'  # URL of main webpage
    pokemon_urls: List[str] = get_pokemon_urls( main_page_URL )  # Get URLs of individual Pokémon pages

    # Create a folder to store JSON files if it doesn't exist
    folder_name: str = 'pokemon_data'
    if not os.path.exists( folder_name ):
        os.makedirs( folder_name )

    # Scrape data for each Pokémon and save to JSON files inside the folder
    for index, pokemon_url in enumerate( pokemon_urls, start=1 ):
        original_id, pokemon_data = scrape_pokemon_details( pokemon_url )  # Scrape details
        # Add a JSON key to the data
        pokemon_data_with_key: Dict[str, Any] = {original_id: pokemon_data}
        # Save data to a JSON file inside the folder
        file_path: str = os.path.join( folder_name, f'pokemon_{original_id}.json' )
        with open( file_path, 'w' ) as file:
            json.dump( pokemon_data_with_key, file, indent=2 )  # Use the data with the added key

    print( 'Data for the first 10 Pokémon has been saved to JSON files in the folder:', folder_name )


if __name__ == "__main__":
    main()
