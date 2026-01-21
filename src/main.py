import tkinter as tk
from gui_app import FloydApp

if __name__ == "__main__":
    # Create the root window
    root = tk.Tk()

    # Initialize  app
    app = FloydApp(root)

    # Start the GUI Loop
    root.mainloop()
