import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from screens.tela_login import TelaLogin

if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()
