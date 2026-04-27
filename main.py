import sys
from dotenv import load_dotenv
load_dotenv()

from PySide6.QtWidgets import QApplication
from spotify_engine import SpotifyController
from ui_island import LoosePickIsland

def main():
    app = QApplication(sys.argv)
    
    # Initialize Spotify
    try:
        spotify_logic = SpotifyController()
    except Exception as e:
        print(f"Spotify Auth Failed: {e}")
        return

    # Initialize UI
    window = LoosePickIsland(spotify_logic)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()