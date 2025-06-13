# Country Leaders Scraper

A Python web scraping project that retrieves information about country leaders from an API and enriches the data with Wikipedia content.

## 📋 Overview

This project fetches country leaders' data from the `country-leaders.onrender.com` API and enhances it by scraping the first paragraph from each leader's Wikipedia page. The scraped content is cleaned and processed to remove unwanted elements like references, phonetic transcriptions, and HTML artifacts.

## 🚀 Features

- **API Integration**: Connects to country-leaders API with proper cookie handling
- **Wikipedia Scraping**: Extracts and cleans first paragraphs from Wikipedia pages
- **Data Cleaning**: Removes references, HTML tags, phonetic transcriptions, and other artifacts
- **Session Management**: Efficient handling of HTTP sessions and cookie renewal
- **Error Handling**: Automatic cookie refresh when sessions expire
- **JSON Export**: Saves processed data to JSON files for further use
- **CSV Export**: Saves processed data to CSV files ( if '--format csv' is used) for further use

## 📁 Project Structure

```
├── leaders_scraper.py          # Functional implementation
├── leaders_scraper_OO.py       # Object-oriented implementation
├── leaders_scrapper_OO_CSV.py  # Same with CSV exportation possible
├── requirements.txt            # Python dependencies
├── leaders.json                # Output from functional version
├── leaders_byOO.json           # Output from OO version (JSON format)
├── leaders_byOO.csv            # Output from OO version (CSV format)
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Required packages listed in `requirements.txt`

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4 lxml pandas
```

### Clone the Repository

```bash
git clone https://github.com/Reigen-cs/Wikipedia_scraper.git
cd Wikipedia_scraper
```

## 💻 Usage

### Functional Version

```bash
python leaders_scraper.py
```

### Object-Oriented Version

```bash
# Save as JSON (default)
python leaders_scraper_OO.py

# Save as CSV
python leaders_scraper_OO_CSV.py --format csv
```

Each scripts will:
1. Fetch the list of countries from the API
2. Retrieve leader information for each country
3. Scrape and clean Wikipedia content for each leader
4. Save the results to a JSON file (functional version) or JSON/CSV file (OO version)

## 📊 Output Format

### JSON Format
The generated JSON file contains a dictionary structure:

```json
{
  "Country Name": [
    {
      "id": "leader_id",
      "first_name": "First",
      "last_name": "Last",
      "birth_date": "YYYY-MM-DD",
      "death_date": "YYYY-MM-DD",
      "place_of_birth": "City, Country",
      "wikipedia_url": "https://en.wikipedia.org/wiki/...",
      "first_paragraph": "Cleaned Wikipedia first paragraph...",
      "wiki_paragraph": "Cleaned Wikipedia first paragraph..."
    }
  ]
}
```

### CSV Format (OO Version Only)
The CSV file flattens the data structure:

| country | id | first_name | last_name | birth_date | death_date | place_of_birth | wikipedia_url | wiki_paragraph |
|---------|----|-----------|-----------|-----------|-----------|-----------|-----------|-----------
| Belgium | leader_1 | First | Last | 1970-01-01 | | Brussels, Belgium | https://... | Biography text... |

## 🧹 Data Cleaning Features

The scraper includes comprehensive text cleaning:

- **Reference Removal**: Strips `[1]`, `[2]` style citations
- **HTML Tag Removal**: Eliminates remaining HTML markup
- **Phonetic Cleaning**: Removes phonetic transcriptions like `[ˈɡi vɛʁɔfstat]`
- **Link Cleanup**: Removes markdown-style links `[text](url)`
- **Whitespace Normalization**: Standardizes spacing and removes extra newlines
- **Language-Specific**: Handles multilingual elements like "Écouter" and "uitspraak"
- **Symbol Removal**: Strips special symbols like `ⓘ`

## 🔧 Technical Implementation

### Key Components

1. **Cookie Management**: Automatic handling of session cookies with renewal on expiration
2. **Session Optimization**: Reuses HTTP sessions for better performance
3. **Error Handling**: Robust handling of API failures and network issues
4. **Content Parsing**: BeautifulSoup-based HTML parsing for Wikipedia content
5. **Regular Expressions**: Advanced regex patterns for text cleaning

### Architecture Differences

- **leaders_scraper.py**: Functional approach with straightforward execution flow
- **leaders_scraper_OO.py**: Object-oriented design with better separation of concerns and type hints

## 🚦 Error Handling

The scraper includes several error handling mechanisms:

- Automatic cookie refresh when API returns 403 status
- Graceful handling of missing Wikipedia content
- Session management for reliable HTTP requests
- Data validation for saved  files

## 🔗 API Reference

The project uses the Country Leaders API available at:
- Base URL: `https://country-leaders.onrender.com`
- Endpoints:
  - `/status` - API status
  - `/countries` - List of available countries
  - `/cookie` - Get session cookie
  - `/leaders` - Get leaders for a specific country
