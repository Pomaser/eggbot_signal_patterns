import sys
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from generation import Generation
from individual import Individual
from svg_renderer import save_svg

# ── Layout constants ──────────────────────────────────────────────────
NUM_INDIVIDUALS = 12
COLS = 2
CANVAS_W = 3200
CANVAS_H = 800
PREVIEW_W = 480
PREVIEW_H = 120
SCALE_X = PREVIEW_W / CANVAS_W
SCALE_Y = PREVIEW_H / CANVAS_H

SVG_DIR = Path(__file__).parent / "svg"

BG = "#f0f0f0"
PREVIEW_BG = "#ffffff"
ACCENT = "#3a7abf"


# ── Individual panel ──────────────────────────────────────────────────

class IndividualPanel(tk.Frame):
    def __init__(self, parent: tk.Widget, individual: Individual, **kw):
        super().__init__(parent, bd=1, relief="solid", bg=BG, **kw)
        self.individual = individual

        self.preview = tk.Canvas(
            self, width=PREVIEW_W, height=PREVIEW_H,
            bg=PREVIEW_BG, highlightthickness=0,
        )
        self.preview.pack(padx=6, pady=(6, 2))

        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", padx=6, pady=(0, 6))

        self._save_btn = tk.Button(
            ctrl, text="Uložit SVG", command=self._save_svg,
            bg=ACCENT, fg="white", relief="flat", padx=8,
        )
        self._save_btn.pack(side="right")

        self.draw()

    def _save_svg(self) -> None:
        SVG_DIR.mkdir(exist_ok=True)
        existing = {p.stem for p in SVG_DIR.glob("organic_*.svg")}
        n = 1
        while f"organic_{n:04d}" in existing:
            n += 1
        path = SVG_DIR / f"organic_{n:04d}.svg"
        try:
            save_svg(self.individual, str(path))
            self._flash_saved(path.name)
        except OSError as exc:
            messagebox.showerror("Chyba", f"Soubor nelze uložit:\n{exc}")

    def _flash_saved(self, filename: str) -> None:
        btn = self._save_btn
        btn.config(text=f"✓ {filename}", bg="#27ae60")
        btn.after(2500, lambda: btn.config(text="Uložit SVG", bg=ACCENT))

    def draw(self) -> None:
        self.preview.delete("all")
        self.preview.create_rectangle(0, 0, PREVIEW_W, PREVIEW_H, fill=PREVIEW_BG, outline="")
        for seg in self.individual.compute_segments(canvas_width=CANVAS_W, canvas_height=CANVAS_H):
            if len(seg) < 2:
                continue
            flat: list[float] = []
            for x, y in seg:
                flat.append(x * SCALE_X)
                flat.append(y * SCALE_Y)
            self.preview.create_line(flat, fill="#1a1a1a", width=1, smooth=False)


# ── Main application ──────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Organic Generator")
        self.configure(bg=BG)
        self.minsize(1020, 600)

        self.generation = Generation(NUM_INDIVIDUALS)
        self.panels: list[IndividualPanel] = []

        self._build_toolbar()
        self._build_scroll_area()
        self._populate()

    def _build_toolbar(self) -> None:
        bar = tk.Frame(self, bg="#2c3e50", pady=6)
        bar.pack(side="top", fill="x")

        tk.Button(
            bar, text="  Nová generace  ", command=self._reset,
            bg="#27ae60", fg="white", font=("sans-serif", 10, "bold"),
            relief="flat", padx=4, pady=2,
        ).pack(side="left", padx=14)

    def _build_scroll_area(self) -> None:
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(outer, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.viewport = tk.Canvas(outer, bg=BG, yscrollcommand=scrollbar.set, highlightthickness=0)
        self.viewport.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.viewport.yview)

        self.inner = tk.Frame(self.viewport, bg=BG)
        self._window_id = self.viewport.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.viewport.bind("<Configure>", self._on_viewport_configure)

        self.bind_all("<Button-4>", lambda e: self.viewport.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda e: self.viewport.yview_scroll(1, "units"))
        self.bind_all("<MouseWheel>", lambda e: self.viewport.yview_scroll(
            int(-1 * (e.delta / 120)), "units"
        ))

    def _on_inner_configure(self, _event: tk.Event) -> None:
        self.viewport.configure(scrollregion=self.viewport.bbox("all"))

    def _on_viewport_configure(self, event: tk.Event) -> None:
        self.viewport.itemconfig(self._window_id, width=event.width)

    def _populate(self) -> None:
        for w in self.inner.winfo_children():
            w.destroy()
        self.panels.clear()

        for i, ind in enumerate(self.generation.individuals):
            row, col = divmod(i, COLS)
            panel = IndividualPanel(self.inner, ind)
            panel.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.panels.append(panel)

        for col in range(COLS):
            self.inner.columnconfigure(col, weight=1)

        self.viewport.yview_moveto(0)

    def _reset(self) -> None:
        self.generation = Generation(NUM_INDIVIDUALS)
        self._populate()


# ── Entry point ───────────────────────────────────────────────────────

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
