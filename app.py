import sys
import threading
import tkinter as tk
from tkinter import ttk

from gui.organic_tab import OrganicTab
from gui.digital_tab import DigitalTab
from gui.kraslice_tab import KrasliceTab

BG = "#f0f0f0"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Generator")
        self.configure(bg=BG)
        self.minsize(1020, 600)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        notebook.add(OrganicTab(notebook), text="  Organic  ")
        notebook.add(DigitalTab(notebook), text="  Digital  ")
        notebook.add(KrasliceTab(notebook), text="  Kraslice  ")


def _watch_stdin(app: App) -> None:
    for line in sys.stdin:
        if line.strip().lower() == "q":
            app.quit()
            break


if __name__ == "__main__":
    app = App()
    t = threading.Thread(target=_watch_stdin, args=(app,), daemon=True)
    t.start()
    app.mainloop()
