# This file is like the "Start" button on a video game console. 
# It tells the computer to open our special toy box!

import sys
import os

# This part helps the computer find all our toy folders, like a map of the house.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from screens.tela_login import TelaLogin

# This is where the magic starts!
if __name__ == "__main__":
    # We create our login screen, which is like the front door of our house.
    app = TelaLogin()
    # This keeps the door open so we can stay and play.
    app.mainloop()

