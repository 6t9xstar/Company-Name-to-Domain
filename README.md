# Company Name to Domain Extractor

A powerful desktop application that extracts valid domain names from company names using anti-CAPTCHA search engines.

## Features

- **Multi-Engine Search**: Uses DuckDuckGo, StartPage, and Brave Search to avoid CAPTCHAs
- **Direct Domain Validation**: Checks common domain patterns for the company name
- **Smart Extraction**: Parses search results to find relevant domains
- **CSV Export**: Export results to CSV files with timestamps
- **User-Friendly GUI**: Clean interface with progress tracking
- **Real-time Validation**: Verifies domain existence before adding to results

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python domain_extractor.py
   ```

2. Enter a company name in the input field
3. Click "Search Domains" to find valid domains
4. View results in the table
5. Export to CSV using the "Export to CSV" button

## How It Works

1. **Direct Pattern Generation**: Creates common domain patterns from the company name
2. **Multi-Engine Search**: Searches multiple anti-CAPTCHA search engines
3. **Domain Extraction**: Parses HTML to extract potential domains
4. **Validation**: Checks if domains actually exist
5. **Deduplication**: Removes duplicate and invalid domains
6. **CSV Export**: Saves results with company name, domain, and source

## Search Sources

- DuckDuckGo (HTML version)
- StartPage
- Brave Search
- Direct domain pattern matching
- HTTP existence verification

## Output Format

The CSV export includes:
- Company Name
- Domain
- Source (where the domain was found)

## Requirements

- Python 3.7+
- Internet connection
- Windows, macOS, or Linux

## Notes

- The application uses rate limiting to avoid being blocked
- Search results are limited to top 10 most relevant domains
- Domain validation uses HTTP HEAD requests for efficiency
