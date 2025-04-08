import os
import json
import re

# Paths
CVE_FILE = "dat/cve.json"
MITRE_FILE = "dat/mitre.json"
HISTORY_FILE = "history.json"
ANALYSIS_OUTPUT_FILE = "temp_analysis.json"

def load_json_file(file_path):
    """Load a JSON file and return the data."""
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[!] Failed to decode JSON from {file_path}.")
        return []

def get_latest_scrape_file():
    """Find the latest sc_result-n.json file."""
    files = [f for f in os.listdir() if re.match(r"sc_result-\d+\.json", f)]
    if not files:
        print("[!] No sc_result-n.json files found.")
        return None
    latest_file = sorted(files, key=lambda x: int(re.findall(r'\d+', x)[0]), reverse=True)[0]
    return latest_file

def analyze_against_local_cve(data_type):
    """Check the local CVE database for risks and mitigations based on data type."""
    cve_data = load_json_file(CVE_FILE)
    for entry in cve_data:
        if entry.get("type", "").lower() == data_type.lower():
            return {
                "possible_risks": entry.get("possible_risks", []),
                "mitigations": entry.get("mitigations", [])
            }
    return {"possible_risks": [], "mitigations": []}

def map_to_mitre(data_type):
    """Map data type to MITRE ATT&CK framework entries."""
    mitre_data = load_json_file(MITRE_FILE)
    for entry in mitre_data:
        if entry.get("type", "").lower() == data_type.lower():
            return {
                "tactic": entry.get("tactic"),
                "technique": entry.get("technique"),
                "description": entry.get("description"),
                "mitigation_id": entry.get("mitigation_id")
            }
    return {}

def extract_data_types_from_history():
    """Pull all unique data types from history.json."""
    history = load_json_file(HISTORY_FILE)
    if not history:
        return []

    data_types = set()
    for entry in history.get("history", []):
        for item in entry.get("inputs", []):
            data_type = item.get("data_value")
            if data_type:
                data_types.add(data_type.strip().lower())
    return list(data_types)

def perform_threat_analysis(_):
    print("\n[+] Starting threat analysis...")

    latest_file = get_latest_scrape_file()
    if not latest_file:
        print("[!] Cannot proceed with analysis. No scrape result found.")
        return

    scrape_results = load_json_file(latest_file)
    if not scrape_results or not scrape_results.get("results"):
        print("[!] No usable results in scrape file.")
        return

    data_types = extract_data_types_from_history()
    if not data_types:
        print("[!] Could not identify data types from history.")
        return

    full_analysis = []

    for threat in scrape_results["results"]:
        searched_for = threat.get("searched_for", [])
        if not isinstance(searched_for, list):
            searched_for = [searched_for]

        for data_type in searched_for:
            if data_type.lower() not in data_types:
                continue

            threat_summary = {
                "data_type": data_type,
                "matched_value": threat.get("matched_value"),
                "found_in": threat.get("found_in"),
                "website": threat.get("website"),
                "highlight_link": threat.get("highlight_link")
            }

            # Add CVE info
            local_cve = analyze_against_local_cve(data_type)
            threat_summary.update(local_cve)

            # Add MITRE info
            mitre_mapping = map_to_mitre(data_type)
            threat_summary.update({"mitre_mapping": mitre_mapping})

            full_analysis.append(threat_summary)

    if full_analysis:
        with open(ANALYSIS_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(full_analysis, f, indent=4)
        print(f"\n[✔] Threat analysis complete. Report data saved to {ANALYSIS_OUTPUT_FILE}")
    else:
        print("[✔] Analysis complete. No critical threats found or matched.")

