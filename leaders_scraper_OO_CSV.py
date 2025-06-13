import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
import json
import pandas as pd
import argparse

def main():
    """
    Main function to execute script.
    Gets data of country leaders from "https://country-leaders.onrender.com", then fetches first paragraph from wikipedia page.
    Stores everything in dictionary and saves dictionary to json or csv file based on user preference.

    Args:
        None
    
    Returns:
        None
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape country leaders data and save to JSON or CSV')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', 
                       help='Output format: json (default) or csv')
    args = parser.parse_args()

    # Get data of country leaders, fetch and clean first wiki paragraph, add to and return dictionary 
    # (uses 'get_first_paragraph()' function, which uses 'clean_paragraph()' function)
    leaders_per_country = get_leaders()

    # Save dictionary as json or csv file and check output
    save(leaders_per_country, format_type=args.format)

def clean_paragraph(text: str) -> str:
    """
    Removes unwanted patterns from text.

    Args:
        text(str): Wikipedia paragraph with patterns to be removed, such as phonetic script, web symbols, remaining empty brackets or whitespace.

    Returns:
        cleaned_text(str): Cleaned wikipedia paragraph.
    """
    
    # Remove specific unwanted patterns:
    cleaned_text = re.sub(
        r'\[.*?\]'                # Content within square brackets
        r'|/[^/]+/;?'             # Content between slashes with optional trailing semicolon
        r'|(?:\b(?:Écouter|uitspraak)\b;?)'  # Remove "Écouter" and "uitspraak" optionally followed by ";"
        r'|;\s*$',                # Standalone semicolon at the end of the text or line
        '', 
        text
    )
    # Remove remaining ⓘ
    cleaned_text = re.sub(r'ⓘ', '', cleaned_text)

    # Normalize spaces around punctuation and parentheses
    cleaned_text = re.sub(r'\(\s+', '(', cleaned_text)  # Remove space after opening parentheses
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Normalize whitespace
    
    # Remove any empty parentheses and space before commas at the end
    cleaned_text = re.sub(r'\(\s*\)', '', cleaned_text)  # Empty parentheses like "()" or "( )"
    cleaned_text = re.sub(r'\s+,', ',', cleaned_text)  # Remove spaces before commas
    cleaned_text = re.sub(r'\(\s*;\s*', '(', cleaned_text)  # Specifically remove "; " in parentheses
    
    return cleaned_text

def get_first_paragraph(wikipedia_url: str, session: requests.Session) -> Optional[str]:
    """
    Fetches the first paragraph from a Wikipedia URL using a given session.

    Args:
        wikipedia_url (str): The Wikipedia URL of the respective state leader.
        session (requests.Session): A session object to make the request.

    Returns:
        Optional[str]: Cleaned first paragraph from the Wikipedia page, or None if not found.
    """

    # Use session to make request
    req = session.get(wikipedia_url)
    soup = BeautifulSoup(req.content, "html.parser")
    # Get list of paragraphs
    paragraphs = [tag for tag in soup.find_all("p")]
    # Get index of first paragraph
    par_index = next(
        (i for i, tag in enumerate(paragraphs) if tag.find("b") is not None),
        None
    )
    # Clean paragraph and return, if found, otherwise return None
    return clean_paragraph(paragraphs[par_index].text) if par_index is not None else None

def get_leaders() -> dict:
    """
    Gets data of country leaders retrieved from "https://country-leaders.onrender.com",
    accesses wiki page using session , gets and cleans first paragraph.

    Args: None

    Returns:
        dict: Dictionary of countries and information on their respective leaders incl. first paragraph of wikipedia article.
    """
    # Define URLs
    root_url = "https://country-leaders.onrender.com"
    countries_url = root_url + "/countries"
    cookie_url = root_url + "/cookie"
    leaders_url = root_url + "/leaders"

    # Create a session for Wikipedia requests
    session = requests.Session()

    # Get Cookies
    cookies = session.get(cookie_url).cookies
    
    # Get Countries
    countries = session.get(countries_url, cookies=cookies).json()
    
    # Initialize dictionary
    leaders_per_country = {}
    
    # Outer loop: Iterate over countries
    for country in countries:

        # Check, if the cookies are expired (response code 403 instead of 200)
        response = session.get(leaders_url, cookies=cookies, params={"country":country})

        if response.status_code != 200:
            # Refresh cookies
            cookies = session.get(cookie_url).cookies
            # Renew request
            leaders_per_country[country] = session.get(leaders_url, cookies=cookies, params={"country": country}).json()
        else:
            # Use response data: Get leaders' data and add to dict
            leaders_per_country[country] = response.json()

        # Inner loop: Iterate over leaders
        for leader_dict in leaders_per_country[country]:
            # Get wiki url
            wiki_url = leader_dict["wikipedia_url"]
            # Use session to get the first paragraph from Wiki (cleaning incl.)
            first_paragraph = get_first_paragraph(wiki_url, session)
            # Add cleaned paragraph to leaders dictionary
            leader_dict["wiki_paragraph"] = first_paragraph
    
    return leaders_per_country

def convert_to_dataframe(leaders_per_country: dict) -> pd.DataFrame:
    """
    Converts the nested dictionary structure to a flat pandas DataFrame.

    Args:
        leaders_per_country (dict): Dictionary containing data of state leaders per country.

    Returns:
        pd.DataFrame: Flattened DataFrame with country information included.
    """
    rows = []
    
    for country, leaders in leaders_per_country.items():
        for leader in leaders:
            # Create a row with country information
            row = {'country': country}
            row.update(leader)
            rows.append(row)
    
    return pd.DataFrame(rows)

def save(leaders_per_country: dict, format_type: str = 'json') -> None:
    """
    Saves a dictionary of state leader data to a json or csv file, reloads the file to check the content and prints out a message, 
    informing, whether or not the saving process was successful.

    Args:
        leaders_per_country (dict): Dictionary containing data of state leaders per country.
        format_type (str): Either 'json' or 'csv' to specify output format.

    Return:
        None
    """
    if format_type.lower() == 'csv':
        # Convert to DataFrame and save as CSV
        df = convert_to_dataframe(leaders_per_country)
        filename = "leaders_byOO.csv"
        df.to_csv(filename, index=False, encoding="utf-8")
        
        # Read back and verify
        try:
            loaded_df = pd.read_csv(filename, encoding="utf-8")
            if loaded_df.shape == df.shape and not loaded_df.empty:
                print(f"The CSV file '{filename}' was saved and checked successfully.")
                print(f"Saved {len(loaded_df)} leaders from {loaded_df['country'].nunique()} countries.")
            else:
                print("Error: Content of CSV file does not match expected dimensions.")
        except Exception as e:
            print(f"Error reading back CSV file: {e}")
    
    else:  # Default to JSON
        filename = "leaders_byOO.json"
        # Save dictionary to json file
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(leaders_per_country, json_file, indent=4, ensure_ascii=False)
        
        # Read the data back from leaders.json
        try:
            with open(filename, "r", encoding="utf-8") as json_file:
                loaded_data = json.load(json_file)
            
            # Check, if the content loaded is the same as the original dictionary
            if loaded_data == leaders_per_country:
                print(f"The JSON file '{filename}' was saved and checked successfully.")
                total_leaders = sum(len(leaders) for leaders in leaders_per_country.values())
                print(f"Saved {total_leaders} leaders from {len(leaders_per_country)} countries.")
            else:
                print("Error: Content of output file does not match. There may be an issue with saving/loading.")
        except Exception as e:
            print(f"Error reading back JSON file: {e}")

# Execute main()
if __name__ == "__main__":
    main()