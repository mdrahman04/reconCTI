import os
import json
import requests
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
from collections import defaultdict
from scripts.tor_connection import get_tor_session

# Constants
SCRAPE_RESULTS_FILE = "scrape_results.json"
MAX_MATCHES_PER_PAGE = 10
DEFAULT_MAX_DEPTH = 2


def load_existing_results():
    if not os.path.exists(SCRAPE_RESULTS_FILE):
        return {"results": []}

    try:
        with open(SCRAPE_RESULTS_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else {"results": []}
    except (json.JSONDecodeError, IOError):
        print("[!] Warning: Existing results file is empty or corrupted. Creating a new one.")
        return {"results": []}


def get_next_result_filename():
    existing_files = [f for f in os.listdir() if f.startswith("sc_result-") and f.endswith(".json")]
    next_number = len(existing_files) + 1
    return f"sc_result-{next_number}.json"


def save_results(data, separate=False):
    file_name = SCRAPE_RESULTS_FILE if not separate else get_next_result_filename()
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"\n[+] Results saved to {file_name}")


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def generate_highlight_link(url, text):
    encoded_text = quote(text)
    return f"{url}#body:~:text={encoded_text}"


def find_similar_data(html, search_values, search_mode):
    soup = BeautifulSoup(html, "lxml")
    matches = defaultdict(list)
    found_texts = set()

    for tag in soup.find_all(["p", "span", "div", "td", "li", "a"]):
        text = tag.get_text(separator=" ", strip=True)

        if search_mode == "or":
            for value in search_values:
                if value.lower() in text.lower() and text not in found_texts:
                    matches[value].append(tag)
                    found_texts.add(text)
                    if len(matches[value]) >= MAX_MATCHES_PER_PAGE:
                        break

        elif search_mode == "and":
            if all(value.lower() in text.lower() for value in search_values) and text not in found_texts:
                key = " & ".join(search_values)
                matches[key].append(tag)
                found_texts.add(text)
                if len(matches[key]) >= MAX_MATCHES_PER_PAGE:
                    break

    return matches


def scrape_single_website(url, search_values, search_mode, onion_links, max_depth):
    visited_urls = defaultdict(int)
    seen_links = set()
    results = []
    root_parsed = urlparse(url)
    root_path = root_parsed.path.rstrip("/") or "/"
    root_domain = root_parsed.netloc
    session = get_tor_session() if onion_links == "yes" else requests.Session()

    def is_within_root_path(link):
        parsed_link = urlparse(link)
        return parsed_link.path.startswith(root_path)

    def crawl(current_url, depth):
        if visited_urls[current_url] >= 2 or depth > max_depth:
            return
        visited_urls[current_url] += 1

        try:
            print(f"[*] Scraping: {current_url}")
            response = session.get(current_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] Failed to access {current_url}: {e}")
            return

        soup = BeautifulSoup(response.text, "lxml")
        matches = find_similar_data(response.text, search_values, search_mode)

        for key, tags in matches.items():
            for tag in tags:
                text = tag.get_text(separator=" ", strip=True)
                highlight_link = generate_highlight_link(current_url, text)

                if highlight_link not in seen_links:
                    results.append({
                        "searched_for": search_values,
                        "matched_value": key,
                        "found_in": tag.name,
                        "website": current_url,
                        "highlight_link": highlight_link
                    })
                    seen_links.add(highlight_link)

        for a_tag in soup.find_all("a", href=True):
            link = urljoin(current_url, a_tag["href"])
            if is_valid_url(link) and urlparse(link).netloc == root_domain and is_within_root_path(link):
                crawl(link, depth + 1)

    crawl(url, depth=0)
    return results


def scrape_website(search_data):
    search_values = [entry["data_value"] for entry in search_data["inputs"]]
    search_mode = search_data["search_mode"]
    onion_links = search_data["onion_links"]
    websites = search_data["websites"]

    try:
        max_depth = int(input(f"[?] Enter max depth for scanning (default {DEFAULT_MAX_DEPTH}): ").strip() or DEFAULT_MAX_DEPTH)
    except ValueError:
        max_depth = DEFAULT_MAX_DEPTH

    print("\n[+] Starting the scraping process...\n")

    all_results = load_existing_results()
    new_results = {"results": []}

    for website in websites:
        results = scrape_single_website(website, search_values, search_mode, onion_links, max_depth)
        new_results["results"].extend(results)

    all_results["results"].extend(new_results["results"])
    save_results(all_results)

    save_separate = input("\n[?] Do you want to save an additional results file? (yes/no): ").strip().lower()
    if save_separate == "yes":
        save_results(new_results, separate=True)

    print("\n[✔] Scraping completed!")
