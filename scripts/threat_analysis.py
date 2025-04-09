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

def extract_latest_data_values_and_types():
    """Extract data values and their corresponding types from the latest entry in history.json."""
    history_data = load_json_file(HISTORY_FILE)
    if not history_data or "searches" not in history_data or not history_data["searches"]:
        return []

    last_entry = history_data["searches"][-1]
    inputs = last_entry.get("inputs", [])
    return [(i.get("data_value", "").strip().lower(), i.get("data_type", "").strip()) for i in inputs]

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

    inputs = extract_latest_data_values_and_types()
    if not inputs:
        print("[!] Could not extract data values from history.")
        return

    full_analysis = []

    for threat in scrape_results["results"]:
        matched_value = threat.get("matched_value", "").strip().lower()

        for input_value, input_type in inputs:
            if matched_value == input_value:
                threat_summary = {
                    "data_type": input_type,
                    "matched_value": matched_value,
                    "found_in": threat.get("found_in"),
                    "website": threat.get("website"),
                    "highlight_link": threat.get("highlight_link")
                }

                # Add CVE info
                local_cve = analyze_against_local_cve(input_type)
                threat_summary.update(local_cve)

                # Add MITRE info
                mitre_mapping = map_to_mitre(input_type)
                threat_summary["mitre_mapping"] = mitre_mapping

                full_analysis.append(threat_summary)
                break  # No need to check further if match found

    # Write analysis JSON file even if empty
    with open(ANALYSIS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_analysis, f, indent=4)

    if full_analysis:
        print(f"\n[✔] Threats detected. Report saved to {ANALYSIS_OUTPUT_FILE}")
    else:
        print("[✔] Analysis complete. No threats matched, but report still saved.")
