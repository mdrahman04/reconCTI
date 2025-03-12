import os
import re
import json
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
from scripts.tor_connection import check_tor_status, get_tor_session  # Import Tor utilities

# Global variables
SCRAPE_RESULTS_FILE = "scrape_results.json"


def load_existing_results():
    """Load existing scrape results to avoid duplicates."""
    if not os.path.exists(SCRAPE_RESULTS_FILE):
        return {"results": []}
    with open(SCRAPE_RESULTS_FILE, "r") as f:
        return json.load(f)


def save_results(data, separate=False):
    """Save the scrape results to a JSON file."""
    if separate:
        count = 1
        while os.path.exists(f"sc_result-{count}.json"):
            count += 1
        file_name = f"sc_result-{count}.json"
    else:
        file_name = SCRAPE_RESULTS_FILE

    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\n[+] Results saved to {file_name}")


def is_valid_url(url):
    """Check if a URL is valid."""
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    except ValueError:
        return False


def extract_text_from_html(html):
    """Extract and clean text from HTML content."""
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator=" ", strip=True)


def find_similar_data(html, search_values, search_mode):
    """Find similar data in the given HTML content based on user input."""
    soup = BeautifulSoup(html, "lxml")
    matches = defaultdict(list)

    for tag in soup.find_all(["p", "span", "div", "td", "li", "a"]):
        text = tag.get_text(separator=" ", strip=True)
        if search_mode == "or":
            for value in search_values:
                if value.lower() in text.lower():
                    matches[value].append(tag)
        elif search_mode == "and":
            if all(value.lower() in text.lower() for value in search_values):
                matches[" & ".join(search_values)].append(tag)

    return matches


def scrape_website(url, search_values, search_mode, onion_links):
    """Scrape a given website recursively for data."""
    visited_urls = set()
    results = []
    root_domain = urlparse(url).netloc
    session = get_tor_session() if onion_links == "yes" else requests.Session()

    def crawl(current_url):
        """Recursive function to scrape all sub-links under the root domain."""
        if current_url in visited_urls:
            return
        visited_urls.add(current_url)

        try:
            print(f"[*] Scraping: {current_url}")
            response = session.get(current_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            print(f"[!] Failed to access {current_url}")
            return

        soup = BeautifulSoup(response.text, "lxml")
        matches = find_similar_data(response.text, search_values, search_mode)

        for key, tags in matches.items():
            for tag in tags:
                link_to_match = f"{current_url}#{tag.name}"  # Highlight match
                results.append({
                    "searched_for": search_values,
                    "matched_value": key,
                    "found_in": tag.name,
                    "website": current_url,
                    "highlight_link": link_to_match
                })

        # Extract new links within the same domain
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(current_url, a_tag["href"])
            if is_valid_url(link) and urlparse(link).netloc == root_domain:
                crawl(link)

    crawl(url)
    return results


def start_scraper(search_data):
    """Initiate the scraping process."""
    search_values = [entry["data_value"] for entry in search_data["inputs"]]
    search_mode = search_data["search_mode"]
    onion_links = search_data["onion_links"]
    websites = search_data["websites"]

    print("\n[+] Starting the scraping process...\n")

    all_results = load_existing_results()

    for website in websites:
        results = scrape_website(website, search_values, search_mode, onion_links)
        all_results["results"].extend(results)

    save_results(all_results)

    # Ask if user wants to save a separate file
    save_separate = input("\n[?] Do you want to save an additional results file? (yes/no): ").strip().lower()
    if save_separate == "yes":
        save_results(all_results, separate=True)

    print("\n[✔] Scraping completed!")

