#!/usr/bin/env python3
"""
Amazon Niche Finder - Discover low-competition niches on Amazon.
Author: Nick G.
Version: 1.0
Website: gm-sunshine.com
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random
import logging
import re
import argparse
from typing import List, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration Constants
MAX_RETRIES = 3
BACKOFF_FACTOR = 1
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
REQUEST_TIMEOUT = 10
MIN_DELAY = 2  # Minimum delay between requests
MAX_DELAY = 7  # Maximum delay between requests
LOW_COMPETITION_THRESHOLD = 2000  # Maximum results to be considered low competition

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('amazon_niche_finder.log')
    ]
)
logger = logging.getLogger(__name__)

# Configure session with retries
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_CODES
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session

BASE_URL = "https://www.amazon.com/s"
SUGGESTION_URL = "https://completion.amazon.com/api/2017/suggestions"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}

# STEP 1: Get keyword suggestions from Amazon
def get_suggestions(session: requests.Session, seed="coloring book for") -> List[str]:
    try:
        # Each suggestion-type needs to be a separate parameter
        params = {
            "limit": "11",
            "prefix": seed,
            "suggestion-type[]": ["WIDGET", "KEYWORD"],  # Changed to suggestion-type[]
            "page-type": "Detail",
            "alias": "stripbooks",
            "site-variant": "desktop",
            "version": "3",
            "event": "onkeypress",
            "wc": "",
            "lop": "en_US",
            "last-prefix": "",
            "avg-ks-time": "1989",
            "fb": "1",
            "session-id": "137-1927523-7967027",
            "client-info": "search-ui",
            "mid": "ATVPDKIKX0DER",
            "plain-mid": "1",
        }
        
        # Convert parameters to URL format manually to handle the array parameter correctly
        param_parts = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    param_parts.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(v)}")
            else:
                param_parts.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(str(value))}")
        
        url = f"{SUGGESTION_URL}?{'&'.join(param_parts)}"
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        # Extract suggestions from new API format
        if isinstance(data, dict) and "suggestions" in data:
            return [item["value"] for item in data["suggestions"] if "value" in item]
        logger.warning("Unexpected response format from suggestions API")
        return []
    except requests.RequestException as e:
        logger.error(f"Error fetching suggestions: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_suggestions: {str(e)}")
        logger.error(f"Response content: {response.text if 'response' in locals() else 'No response'}")
        return []

# STEP 2: Get result count from Amazon search page
def get_result_count(session: requests.Session, keyword: str) -> int:
    try:
        search_url = f"{BASE_URL}?k={urllib.parse.quote_plus(keyword)}"
        response = session.get(search_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try multiple possible selectors for result count
        selectors = [
            ("span", {"data-component-type": "s-result-info-bar"}),
            ("div", {"class": "sg-col-inner"}),
            ("div", {"class": "a-section a-spacing-small a-spacing-top-small"})
        ]

        for tag, attrs in selectors:
            result_text = soup.find(tag, attrs)
            if result_text:
                text = result_text.get_text()
                # Try different result patterns
                patterns = [
                    r'(\d[\d,]*)\s+results',
                    r'(\d[\d,]*)\s+Results',
                    r'over\s+(\d[\d,]*)',
                    r'(\d[\d,]*)\s+product'
                ]
                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        return int(match.group(1).replace(',', ''))
        
        logger.warning(f"Could not find result count for: {keyword}")
        return -1
    except requests.RequestException as e:
        logger.error(f"Request error for {keyword}: {str(e)}")
        return -1
    except Exception as e:
        logger.error(f"Unexpected error for {keyword}: {str(e)}")
        return -1

# STEP 3: Run niche discovery
def discover_niches(seed: str) -> List[Tuple[str, int]]:
    logger.info(f"🔍 Seed: {seed}")
    session = create_session()
    
    suggestions = get_suggestions(session, seed)
    if not suggestions:
        logger.error("No suggestions found. The request might have been blocked.")
        return []
        
    results = []
    for suggestion in suggestions:
        # Random delay between 2 and 7 seconds to avoid rate limiting
        time.sleep(MIN_DELAY + random.random() * (MAX_DELAY - MIN_DELAY))
        count = get_result_count(session, suggestion)
        logger.info(f"{suggestion} → {count if count != -1 else '❌ Not Found'} results")
        results.append((suggestion, count))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find low-competition niches on Amazon')
    parser.add_argument('--seed', default='coloring book for',
                      help='Seed keyword to search for (default: "coloring book for")')
    parser.add_argument('--threshold', type=int, default=LOW_COMPETITION_THRESHOLD,
                      help=f'Maximum results to be considered low competition (default: {LOW_COMPETITION_THRESHOLD})')
    args = parser.parse_args()

    try:
        niche_results = discover_niches(args.seed)

        if not niche_results:
            logger.error("No results found. Please try a different seed keyword or check your internet connection.")
            exit(1)

        # Filter low-competition niches
        low_comp = [r for r in niche_results if 0 < r[1] < args.threshold]
        
        print(f"\n💡 Low Competition Niches (under {args.threshold} results):")
        # Log to a separate file
        with open('discovered_niches.log', 'a', encoding='utf-8') as f:
            f.write(f"\n💡 Low Competition Niches (under {args.threshold} results):\n")
            if low_comp:
                for keyword, count in sorted(low_comp, key=lambda x: x[1]):
                    line = f"{keyword} → {count:,} results\n"
                    print(line, end='')
                    f.write(line)
            else:
                print("No low-competition niches found. Try a different seed keyword or increase the threshold.")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        exit(0)
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        exit(1)
