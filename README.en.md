# AirfoilMatic V0.6.7 Beta — 2D CFD Domain Generator

[Türkçe](README.md) | **English**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://airfoilmatic.streamlit.app/)
[![tests](https://github.com/meceylan/AirfoilMatic/actions/workflows/tests.yml/badge.svg)](https://github.com/meceylan/AirfoilMatic/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Pick an airfoil; AirfoilMatic builds the flow domain around it for a 2D analysis in Ansys Fluent (C-grid or rectangular, six four-sided blocks), gives you the geometry for DesignModeler / SpaceClaim or a ready Fluent mesh file (.msh), and works out the mesh settings for your y⁺ and the values to enter in Fluent.

**[Run it in your browser → airfoilmatic.streamlit.app](https://airfoilmatic.streamlit.app/)** (no installation)

<!-- Screenshot: once docs/img/app.png is added, remove the comment markers around the next line.
![AirfoilMatic interface](docs/img/app.png)
-->

## Features
* **Airfoil:** NACA 4 / 5-digit (from the equations), 300 sections selected from the UIUC database (suggestions while typing, 🎲 random section) or your own `.dat` / `.txt` / `.csv` file (Selig, Lednicer; units, origin and point order do not matter). The app does not invent sections: a name that is not listed is reported as not in the database.
* **Domain and geometry:** C-grid or rectangular domain, 6 four-sided blocks; DesignModeler TXT and SpaceClaim TXT; SolidWorks ZIP for the section alone; **m / mm** output unit.
* **Fluent mesh file (.msh):** the app builds the mapped mesh of the C-grid or rectangular domain itself (transfinite interpolation; boundaries `inlet`, `outlet`, `wall`); no DesignModeler or Meshing needed. Up to 1 000 000 cells.
* **Mesh / y⁺:** first-cell height for a target y⁺; Ansys Inflation settings or an Edge Sizing table for a mapped mesh; mesh quality check; y⁺ correction from a first Fluent result.
* **Mesh independence:** coarse / medium / fine meshes in one ZIP (cell sizes by √2), **GCI** from the report files (Celik et al. 2008).
* **Flow and Fluent helper:** Reynolds, Mach + Reynolds + temperature, or speed + density + viscosity; inlet velocity components, Lift/Drag vectors, reference values, turbulence decay.
* **Automation:** angle-of-attack sweep (even steps or your own list), a Fluent journal (`.jou`) that steps the `aoa` expression, polar from the report file (Cl–α, Cd–α, Cl–Cd).
* **Use-as-drawn mode:** an uploaded outline is used in its own point order; for VGs, flaps or kinked sections (inflation only; tried in Fluent 2024 R2 with NACA 4412).
* Save / load settings as a JSON file; Turkish / English interface.

## How to use it
1. **Pick an airfoil:** search box, 🎲 or your own file.
2. **Enter the domain and flow:** domain type and size (in chords), Reynolds or Mach, target y⁺.
3. **Get the mesh**, one of two ways:
   * download the app's `.msh` file and open it in Fluent with `File → Read → Mesh`, or
   * import the TXT into DesignModeler / SpaceClaim and mesh with Inflation or Mapped in Ansys Meshing (steps below).
4. **Set up and run Fluent:** enter the values from the Fluent helper; run the angle sweep with the journal from the Automation tab, then upload the report file for the polar and the GCI.

<details>
<summary><b>Ansys DesignModeler / Meshing steps</b></summary>

1. **Import:** In DesignModeler, first set `Units` to the output unit chosen in the sidebar (`Meter` for m, `Millimeter` for mm), then use `Concept > 3D Curve`, select the downloaded `.txt` file and click `Generate`.
2. **Surface:** Use `Concept > Surfaces from Edges` with the outer boundary and airfoil edges to create the flow surface.
3. **Split:** Use `Tools > Projection` with the exported split lines.
4. **Mesh:** the **Mesh / y⁺** tab gives the settings for both workflows.
   * **Inflation (quad-dominant):** export the front axis + wake axis (or all six lines); a single line, or the wake axis without the front axis, makes inflation fail. Add `Inflation` on all faces with the airfoil edges **and the wake axis** as boundary, set the global Element Size to about 0.5c and enter the Edge Sizings from the table. Use a sharp trailing edge; blunt TE + inflation failed in our tests.
   * **Mapped:** export all six split lines, add `Face Meshing` (Mapped) to all faces and the `Edge Sizing` values from the table. One common bias on wall-normal edges with the same number of divisions changes the first cell by at most 2 %.
   * Inflation and Mapped Face Meshing cannot be combined on the same face.
5. **Check:** Fluent reports y⁺ at the cell centroid, so expect about half the target value.
6. **Changing the mesh:** read the set-up case, type `/mesh/replace` in the console and give the file name with its extension (`name.msh`). With the same zone names (`inlet`, `outlet`, `wall`) the boundary conditions, expressions and reports are kept; then initialise. Tried in Fluent 2024 R2.

Why split the airfoil at X = 0.3c? It separates the high-curvature leading-edge region, the vertical split lines meet the outer boundary at right angles (no sliver faces), and every block stays four-sided (for mapped meshing). Details: [docs/VALIDATION.en.md](docs/VALIDATION.en.md#why-split-at-x--03c).
</details>

## What was tried in Ansys?
| What | Where | Result |
|---|---|---|
| The app's `.msh`, C-grid | Fluent 2024 R2, NACA 4412, −4…8° | Mesh Check without errors; Cl / Cd within 0.01 % / 0.05 % of the Ansys mesh |
| The app's `.msh`, rectangle | Fluent 2024 R2, NACA 4412, −4…8° | Cl within 0.2 % of the C-grid; Cd 1.6 % lower at 8° |
| NACA 0012 vs Ladson's experiment | Fluent 2024 R2, α = 4.25° | Cl within 1 %, Cd within 2–3.5 %; "consistent with the experiment", not a firm validation |
| Mesh independence (GCI) | Fluent 2024 R2, NACA 4412, 4° | the three meshes within 0.1 % |
| Fluent journal | Fluent 2024 R2 (standalone) | works; does not work inside Workbench |
| Domain DesignModeler TXT and SpaceClaim TXT; section SolidWorks ZIP and SpaceClaim TXT | user | tried |
| Section-only DesignModeler TXT | — | not tried yet |
| Case overwriting in the journal | — | not tried yet |

Setups, tables and all the numbers: **[docs/VALIDATION.en.md](docs/VALIDATION.en.md)**.

**Limits:** the mesh plan is built for low speed (Mach < 0.3; no mesh settings specific to compressible flow). At high Cl, enlarge the domain radius and check that the result does not change.

## Local installation
```bash
git clone https://github.com/meceylan/AirfoilMatic.git
cd AirfoilMatic
pip install -r requirements.txt
streamlit run app.py
```
Tests: `pip install pytest`, then `python -m pytest -q`. Python 3.11+, Streamlit, NumPy, Plotly.

## Developer
**Muhammet Emin CEYLAN**, Iskenderun Technical University · [LinkedIn](https://www.linkedin.com/in/muhammet-emin-ceylan-b79847334) · [GitHub](https://github.com/meceylan)

Please use the [Issues](https://github.com/meceylan/AirfoilMatic/issues) page for bugs and suggestions. Changes: [CHANGELOG.md](CHANGELOG.md).

## License
MIT License. The interface font, Source Serif 4, is distributed under the SIL Open Font License 1.1 (`static/fonts/OFL-SourceSerif4.txt`). The coordinates in the section selection come from the [UIUC Airfoil Coordinates Database](https://m-selig.ae.illinois.edu/ads/coord_database.html) maintained by Prof. Michael S. Selig and are not covered by the MIT license; the selection can be rebuilt with `tools/build_airfoil_library.py`.
