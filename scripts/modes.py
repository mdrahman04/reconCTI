import json
import os
import re
from datetime import datetime


def load_history():
    if not os.path.exists("history.json"):
        with open("history.json", "w") as f:
            json.dump({"searches": []}, f, indent=4)
    if os.stat("history.json").st_size == 0:
        with open("history.json", "w") as f:
            json.dump({"searches": []}, f, indent=4)
    with open("history.json", "r") as f:
        return json.load(f)


def save_history(history):
    with open("history.json", "w") as f:
        json.dump(history, f, indent=4)


def add_timestamped_entry(entry):
    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return entry


def guided_mode():
    print("\n[Guided Mode] Please answer the following questions step by step:\n")
    history = load_history()
    search_data = {"time": str(datetime.now()), "inputs": []}

    while True:
        data_type = input("Enter the type of data to search (e.g., Name, Phone, Passport): ").strip()
        if not data_type:
            print("Error: Data type cannot be empty. Please enter a valid type.")
            continue

        data_value = input(f"Enter the {data_type}: ").strip()
        if not data_value:
            print("Error: Data value cannot be empty. Please enter valid data.")
            continue

        search_data["inputs"].append({"data_type": data_type, "data_value": data_value})

        add_more = input("\nDo you want to add more data? (yes or no): ").strip().lower()
        if add_more not in ["yes", "no"]:
            print("Error: Invalid response. Please enter 'yes' or 'no'.")
            continue
        if add_more == "no":
            break

    while True:
        search_mode = input("\nSelect search mode (AND for all keywords, OR for any keyword): ").strip().lower()
        if search_mode not in ["and", "or"]:
            print("Error: Invalid search mode. Please enter 'AND' or 'OR'.")
        else:
            break

    while True:
        onion_links = input("\nWill you need to search onion links? (yes or no): ").strip().lower()
        if onion_links not in ["yes", "no"]:
            print("Error: Invalid response. Please enter 'yes' or 'no'.")
        else:
            break

    if onion_links == "yes":
        import tor  # This will check and start Tor
        tor.start_tor()

    while True:
        websites = input("\nAdd websites to search (comma-separated): ").strip()
        website_list = [site.strip() for site in websites.split(",") if site.strip()]
        if not website_list:
            print("Error: You must provide at least one website.")
        else:
            break

    search_data.update({"search_mode": search_mode, "onion_links": onion_links, "websites": website_list})
    history["searches"].append(search_data)

    save_history(history)
    print("\n[Info] Proceeding to scrape the data ...")


def commando_mode():
    print("\n[Commando Mode] Please input your command as follows:")
    print("\nFormat: <datatypes>, <data>, <search_mode>, <onion_links>, <websites>")
    print('Example: "name, dob", "john, 15 June", "and", "yes", "google.com, yahoo.com"')

    history = load_history()
    search_data = {"time": str(datetime.now())}

    while True:
        command = input("\nEnter your command: ").strip()
        try:
            pattern = r'\"(.*?)\"'
            parts = re.findall(pattern, command)

            if len(parts) != 5:
                raise ValueError("Error: Invalid format. Ensure your input matches the example format.")

            datatypes = [dtype.strip() for dtype in parts[0].split(",")]
            data_values = [dval.strip() for dval in parts[1].split(",")]
            if not datatypes or not data_values:
                raise ValueError("Error: Data types and values cannot be empty.")
            if len(datatypes) != len(data_values):
                raise ValueError("Error: Number of data types and values must match.")

            search_mode = parts[2].lower()
            if search_mode not in ["and", "or"]:
                raise ValueError("Error: Search mode must be 'AND' or 'OR'.")

            onion_links = parts[3].lower()
            if onion_links not in ["yes", "no"]:
                raise ValueError("Error: Onion links query must be 'yes' or 'no'.")

            if onion_links == "yes":
                import tor  # This will check and start Tor
                tor.start_tor()

            websites = [site.strip() for site in parts[4].split(",")]
            if not websites:
                raise ValueError("Error: At least one website must be provided.")

            search_data["inputs"] = [{"data_type": dt, "data_value": dv} for dt, dv in zip(datatypes, data_values)]
            search_data.update({"search_mode": search_mode, "onion_links": onion_links, "websites": websites})
            break

        except ValueError as e:
            print(e)
            continue

    history["searches"].append(search_data)

    save_history(history)
    print("\n[Info] Proceeding to scrape the data ...")
