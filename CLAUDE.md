# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Project — Organic Generator GUI

Located at the repo root. Run with:
```
python app.py
```
No external dependencies — uses only Python stdlib (tkinter, math, random).

**Structure:**
- `app.py` — entry point; creates `ttk.Notebook` with three tabs
- `svg_renderer.py` — `generate_svg()` / `save_svg()` → 3200×800 SVG; accepts any object with `compute_segments()`
- `signals/organic.py` — `Individual` (8-param wave genome + `compute_segments()`) + `Generation`
- `signals/digital.py` — `DigitalIndividual` (square/sawtooth/triangle/PCM/staircase) + `DigitalGeneration`
- `signals/kraslice.py` — `KrasliceIndividual` (zigzag/diamond/waves/chevron/crosshatch) + `KrasliceGeneration`
- `gui/organic_tab.py` — `IndividualPanel` + `OrganicTab`
- `gui/digital_tab.py` — `DigitalPanel` + `DigitalTab`
- `gui/kraslice_tab.py` — `KraslicePanel` + `KrasliceTab`

---

## Processing Project (original reference)

## Project Overview

GA_eggbot is a Processing sketch implementing a Genetic Algorithm for generating organic wave-based designs, intended for output to an [EggBot](http://egg-bot.com/) 3D plotter. Fitness is user-driven: users rate each design (0–1), then evolve the population.

## Running the Sketch

This is a native Processing project — there is no build system or CLI runner.

- Open `src/ga_eggbot/` in the Processing IDE (v3.0+) and click **Run**
- Required library: **ControlP5** (install via Processing → Sketch → Import Library → Add Library)
- EggBot serial output uses `/dev/ttyACM*`; the sketch will run without hardware attached

## Architecture

The sketch is split across four `.pde` files that Processing compiles as a single program:

### `GA_eggbot.pde` — Entry point & UI
- Sets up the ControlP5 UI (sliders, buttons, rating inputs)
- Manages display mode: **generations view** (current population) vs. **lineage view** (best ancestor per generation)
- Key constants: `numIndividuals = 50` (must be even), `mutationProbability = 0.1`, `crossoverProbability = 0.75`

### `Individual.pde` — Genome & rendering
- Each individual has **8 float parameters** (range 0–1) encoding a wave pattern:
  - [0] wave magnitude, [1] wavelength, [2–3] first modulation (amplitude & wavelength), [4–5] second modulation, [6] wave count, [7] modulation count
- `draw()` renders the phenotype using nested sine functions with amplitude modulation
- `mutate()` applies Gaussian perturbations (σ=0.25) per parameter at 10% probability
- **To evolve different designs, modify the parameter encoding and `draw()` method here**

### `Generation.pde` — Population & breeding
- `evaluate()` sorts the population by fitness rating
- `evolve()` performs quartile-based selection (bottom→top quartile weighted 10/20/30/40%) followed by single-point crossover and mutation

### `EggbotCanvas.pde` — Rendering & hardware
- Renders designs at quarter resolution on-screen (500×200px) from a logical 2000×800 canvas
- Sends EBB serial commands (`SP` for pen, `SM` for motor steps) to the EggBot when the print button is used
- Applies a 1.6× width multiplier for egg-shaped coordinate transformation; supports 9 pen colors
