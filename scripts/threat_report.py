import json
import os
from fpdf import FPDF
import webbrowser

ANALYSIS_FILE = "temp_analysis.json"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_FILE = os.path.join(ROOT_DIR, "threat_report.pdf")


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Threat Analysis Report", ln=True, align="C")
        self.set_font("Arial", "", 11)
        self.cell(0, 10, "Generated by ReconCTI", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(2)

    def add_threat_entry(self, data_type, matched_values, websites, risks, mitigations, mitre_mapping):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, f"Data Type: {data_type}")
        self.multi_cell(0, 8, f"Matched Values: {', '.join(set(matched_values))}")
        self.multi_cell(0, 8, f"Websites: {', '.join(set(websites))}")
        self.ln(1)

        if risks:
            self.set_font("Arial", "B", 11)
            self.cell(0, 8, "Possible Risks:", ln=True)
            self.set_font("Arial", "", 11)
            for risk in risks:
                self.multi_cell(0, 7, f" - {risk}")

        if mitigations:
            self.set_font("Arial", "B", 11)
            self.cell(0, 8, "Mitigations:", ln=True)
            self.set_font("Arial", "", 11)
            for m in mitigations:
                self.multi_cell(0, 7, f" - {m}")

        if mitre_mapping:
            self.set_font("Arial", "B", 11)
            self.cell(0, 8, "MITRE Mapping:", ln=True)
            self.set_font("Arial", "", 11)
            self.multi_cell(0, 7, f"Tactic: {mitre_mapping.get('tactic')}")
            self.multi_cell(0, 7, f"Technique: {mitre_mapping.get('technique')}")
            self.multi_cell(0, 7, f"Description: {mitre_mapping.get('description')}")
            self.multi_cell(0, 7, f"Mitigation ID: {mitre_mapping.get('mitigation_id')}")

        self.ln(10)


def generate_pdf_report():
    if not os.path.exists(ANALYSIS_FILE):
        print("[!] Analysis file not found. Please run threat analysis first.")
        return

    with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("[!] No threat data to generate report.")
        return

    grouped = {}
    for entry in data:
        dtype = entry.get("data_type")
        if not dtype:
            continue
        if dtype not in grouped:
            grouped[dtype] = {
                "matched_values": [],
                "websites": [],
                "possible_risks": entry.get("possible_risks", []),
                "mitigations": entry.get("mitigations", []),
                "mitre_mapping": entry.get("mitre_mapping", {})
            }
        grouped[dtype]["matched_values"].append(entry.get("matched_value", ""))
        grouped[dtype]["websites"].append(entry.get("website", ""))

    pdf = PDFReport()
    pdf.add_page()

    for i, (dtype, details) in enumerate(grouped.items(), start=1):
        pdf.section_title(f"Threat #{i}")
        pdf.add_threat_entry(
            data_type=dtype,
            matched_values=details["matched_values"],
            websites=details["websites"],
            risks=details["possible_risks"],
            mitigations=details["mitigations"],
            mitre_mapping=details["mitre_mapping"]
        )

    pdf.output(REPORT_FILE)
    print(f"[✔] Report generated: {REPORT_FILE}")

    try:
        webbrowser.register('firefox', None, webbrowser.BackgroundBrowser('/usr/bin/firefox'))
        webbrowser.get('firefox').open_new_tab(f"file://{REPORT_FILE}")
        print("[✔] Report opened in browser.")
    except Exception as e:
        print(f"[!] Could not open report automatically: {e}")
