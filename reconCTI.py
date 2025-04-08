from scripts.ui import ui_initialization
from scripts.modes import guided_mode, commando_mode
from scripts.threat_analysis import perform_threat_analysis
import os
import json
import re


def get_latest_result_file():
    """Find the most recent 'sc_result-n.json' file."""
    result_files = [f for f in os.listdir() if re.match(r"sc_result-(\d+)\.json", f)]
    if not result_files:
        return None

    # Sort files by numeric value of n in 'sc_result-n.json'
    result_files.sort(key=lambda f: int(re.search(r"sc_result-(\d+)\.json", f).group(1)), reverse=True)
    return result_files[0]


def start_session():
    mode = ui_initialization()
    while True:
        mode = input("Enter your choice (1 or 2): ").strip()
        if mode == '1':
            print("\nYou have selected: Guided Mode")
            guided_mode()
            break
        elif mode == '2':
            print("\nYou have selected: Commando Mode")
            commando_mode()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.\n")

    # Prompt to analyze results
    analyse = input("\n[?] Do you want to analyse the search results? (yes/no): ").strip().lower()
    if analyse == "yes":
        latest_file = get_latest_result_file()
        if latest_file:
            print(f"\n[✔] Using latest result file: {latest_file}")
            try:
                with open(latest_file, "r", encoding="utf-8") as f:
                    all_results = json.load(f)
                    perform_threat_analysis(all_results)
            except (json.JSONDecodeError, IOError):
                print("[!] Failed to load or parse the result file.")
        else:
            print("[!] No saved result files found. Please save results during scraping.")


# Run reconCTI session loop
while True:
    start_session()
    again = input("\n[?] Do you want to start another session? (yes/no): ").strip().lower()
    if again != "yes":
        print("\n[!] Exiting reconCTI...")
        break
