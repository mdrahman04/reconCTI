import os
from scripts.ui import ui_initialization

def main():
    mode = ui_initialization()  # Start UI and get user choice
    if mode == '1':
        print("[*] Guided Mode Selected")
        # Call functions for guided mode (e.g., scrape_website)
    elif mode == '2':
        print("[*] Commando Mode Selected")
        # Directly execute user-provided commands

if __name__ == "__main__":
    main()