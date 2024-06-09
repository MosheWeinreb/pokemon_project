import requests
from bs4 import BeautifulSoup
import json

# Function to get URLs of Pokémon pages
def get_pokemon_urls(URL):
    response = requests.get(URL)  # Send GET request
    response.raise_for_status()    # Check if request was successful
    soup = BeautifulSoup(response.content, 'html.parser')  # Parse webpage content
    # Find links to individual Pokémon pages and construct full URLs
    pokemon_urls = ['https://pokemondb.net' + a['href'] for a in soup.select('.infocard a.ent-name')][:10]
    return pokemon_urls

# Function to extract height or weight from Pokémon's webpage
def extract_measure(soup, measure_name):
    # Find the measure (height/weight) element, extract and convert numeric value
    measure = float(soup.find('table', class_='vitals-table').find('th', string=measure_name).find_next_sibling('td').text.strip().split()[0])
    return measure

# Function to scrape details of each Pokémon
def scrape_pokemon_details(pokemon_url):
    response = requests.get(pokemon_url)    # Send GET request
    response.raise_for_status()
    print (response.status_code)# Check if request was successful
    soup = BeautifulSoup(response.content, 'html.parser')  # Parse webpage content
    # Extract various details: ID, name, types, height, weight, abilities, evolution URL
    id_ = soup.find('table', class_='vitals-table').find('strong').text.strip()
    name = soup.find('h1').text
    types = [a.text for a in soup.find('table', class_='vitals-table').find_all('a', class_='type-icon')]
    height = extract_measure(soup, "Height")  # Extract height
    weight = extract_measure(soup, "Weight")  # Extract weight
    abilities = [a.text for a in soup.find('th', string='Abilities').find_next_sibling('td').find_all('a')]
    evolution_url = pokemon_url
    # Created a dictionary containing the extracted information
    pokemon_data = {
        "id": int(id_),
        "name": name,
        "type": types,
        "height": height,
        "weight": weight,
        "abilities": abilities,
        "evolution": evolution_url
    }
    return pokemon_data

# Main code execution
import os  # Import the os module

# Main code execution
main_page_URL = 'https://pokemondb.net/pokedex/national'  # URL of main webpage
pokemon_urls = get_pokemon_urls(main_page_URL)  # Get URLs of individual Pokémon pages

# Create a folder to store JSON files if it doesn't exist
folder_name = 'pokemon_data'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Scrape data for each Pokémon and save to JSON files inside the folder
for index, pokemon_url in enumerate(pokemon_urls, start=1):
    pokemon_data = scrape_pokemon_details(pokemon_url)  # Scrape details
    # Add a JSON key to the data
    pokemon_data_with_key = {"pokemon": pokemon_data}
    # Save data to a JSON file inside the folder
    file_path = os.path.join(folder_name, f'pokemon_{index}.json')
    with open(file_path, 'w') as file:
        json.dump(pokemon_data_with_key, file, indent=2)  # Use the data with the added key

print('Data for the first 100 Pokémon has been saved to JSON files in the folder:', folder_name)
