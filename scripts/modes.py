import json
import os
import re
from datetime import datetime


def load_history():
    """Load or initialize the history.json file."""
    if not os.path.exists("history.json"):
        with open("history.json", "w") as f:
            json.dump({"searches": []}, f, indent=4)
    # Check if the file is empty
    if os.stat("history.json").st_size == 0:
        with open("history.json", "w") as f:
            json.dump({"searches": []}, f, indent=4)
    # Load the history
    with open("history.json", "r") as f:
        return json.load(f)


def save_history(history):
    """Save data to the history.json file."""
    with open("history.json", "w") as f:
        json.dump(history, f, indent=4)


def add_timestamped_entry(entry):
    """Adds a timestamp to the search entry."""
    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return entry


def guided_mode():
    """Handles step-by-step guided input mode."""
    print("\n[Guided Mode] Please answer the following questions step by step:")
    history = load_history()
    search_data = {"time": str(datetime.now()), "inputs": []}

    while True:
        # Validate data type
        data_type = input("Enter the type of data to search (e.g., name, phone, passport): ").strip()
        if not data_type:
            print("Error: Data type cannot be empty. Please enter a valid type.")
            continue

        # Validate the data
        data_value = input(f"Enter the {data_type}: ").strip()
        if not data_value:
            print("Error: Data value cannot be empty. Please enter valid data.")
            continue

        # Store data type and value
        search_data["inputs"].append({"data_type": data_type, "data_value": data_value})

        # Ask if the user wants to add more
        add_more = input("Do you want to add more data? (yes or no): ").strip().lower()
        if add_more not in ["yes", "no"]:
            print("Error: Invalid response. Please enter 'yes' or 'no'.")
            continue
        if add_more == "no":
            break

    # Validate search mode
    while True:
        search_mode = input("Search mode (AND for all keywords, OR for any keyword): ").strip().lower()
        if search_mode not in ["and", "or"]:
            print("Error: Invalid search mode. Please enter 'AND' or 'OR'.")
        else:
            break

    # Validate onion links query
    while True:
        onion_links = input("Will you need to search onion links? (yes or no): ").strip().lower()
        if onion_links not in ["yes", "no"]:
            print("Error: Invalid response. Please enter 'yes' or 'no'.")
        else:
            break

    # Validate websites
    while True:
        websites = input("Add websites to search (comma-separated): ").strip()
        website_list = [site.strip() for site in websites.split(",") if site.strip()]
        if not website_list:
            print("Error: You must provide at least one website.")
        else:
            break

    # Append the validated inputs to history
    search_data.update({"search_mode": search_mode, "onion_links": onion_links, "websites": website_list})
    history["searches"].append(search_data)

    # Save to JSON
    save_history(history)
    print("\n[Info] Search data saved successfully.")


import re


def commando_mode():
    """Handles input directly from a single command in Commando Mode."""
    print("\n[Commando Mode] Please input your command as follows:")
    print("Format: <datatypes>, <data>, <search_mode>, <onion_links>, <websites>")
    print('Example: "name, dob", "john, 15 June", "and", "yes", "google.com, yahoo.com"')

    history = load_history()
    search_data = {"time": str(datetime.now())}

    while True:
        command = input("\nEnter your command: ").strip()
        try:
            # Use regex to split the command into five main fields
            pattern = r'\"(.*?)\"'  # Matches anything within double quotes
            parts = re.findall(pattern, command)

            if len(parts) != 5:
                raise ValueError("Error: Invalid format. Ensure your input matches the example format.")

            # Extract and validate fields
            datatypes = [dtype.strip() for dtype in parts[0].split(",")]
            data_values = [dval.strip() for dval in parts[1].split(",")]
            if not datatypes or not data_values:
                raise ValueError("Error: Data types and values cannot be empty.")
            if len(datatypes) != len(data_values):
                raise ValueError("Error: Number of data types and values must match.")

            # Validate search mode (case-insensitive)
            search_mode = parts[2].lower()
            if search_mode not in ["and", "or"]:
                raise ValueError("Error: Search mode must be 'AND' or 'OR'.")

            # Validate onion links query
            onion_links = parts[3].lower()
            if onion_links not in ["yes", "no"]:
                raise ValueError("Error: Onion links query must be 'yes' or 'no'.")

            # Validate websites
            websites = [site.strip() for site in parts[4].split(",")]
            if not websites:
                raise ValueError("Error: At least one website must be provided.")

            # Store validated inputs
            search_data["inputs"] = [{"data_type": dt, "data_value": dv} for dt, dv in zip(datatypes, data_values)]
            search_data.update({"search_mode": search_mode, "onion_links": onion_links, "websites": websites})
            break  # Exit the loop on successful input

        except ValueError as e:
            print(e)  # Show a specific error message and ask again
            continue

    # Append the validated inputs to history
    history["searches"].append(search_data)

    # Save to JSON
    save_history(history)
    print("\n[Info] Search data saved successfully.")
