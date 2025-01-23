import time
import sys
import os


def display_ascii_art():
    # Art logo using - https://patorjk.com/
    art = r"""
                              _____ _______ _____ 
                             / ____|__   __|_   _|
  _ __ ___  ___ ___  _ __   | |       | |    | |  
 | '__/ _ \/ __/ _ \| '_ \  | |       | |    | |  
 | | |  __/ (_| (_) | | | | | |____   | |   _| |_ 
 |_|  \___|\___\___/|_| |_|  \_____|  |_|  |_____|                                            
    """
    print(art)
    print("                unleash the sniffer (o_o)\n")


def scanning_effect():
    print("\n[*] Scanning system resources...")
    for _ in range(25):  # Range for longer/shorter animation
        for frame in "|/-\\":
            sys.stdout.write(f"\r[*] Initializing scanner... {frame}")
            sys.stdout.flush()
            time.sleep(0.08)  # Speed of the animation
    print("\r[*] Initializing scanner... Done!      ")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def ui_initialization():
    clear_screen()
    display_ascii_art()
    scanning_effect()

    print("\n\n=================================")
    print("        reconCTI  v1.25")
    print("=================================")
    print("a proactive approach to cyber threat intelligence\n\n")

    print("Select a mode to continue:")
    print("1. Guided Mode - Step-by-step guidance")
    print("2. Commando Mode - Input the whole command directly\n")
