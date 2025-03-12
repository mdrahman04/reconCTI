from scripts.ui import ui_initialization
from scripts.modes import guided_mode, commando_mode

def main():
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

if __name__ == "__main__":
    main()