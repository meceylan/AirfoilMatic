# AirfoilMatic V0.5.3.4 Beta — 2D CFD Domain Generator

[Türkçe](README.md) | **English**

**[Run AirfoilMatic in your browser](https://airfoilmatic-gkxdkjpsclawjnbhmzng89.streamlit.app/)**

AirfoilMatic builds the geometry of a 2D CFD flow domain around an airfoil (NACA 4/5-digit or a custom `.dat` file) and exports it in the Ansys DesignModeler `3D Curve` text format. The domain is already split into six four-sided blocks, so Ansys Meshing can produce a structured (mapped) mesh. It also gives you matching mesh settings (Inflation, Edge Sizing) and Fluent setup values.

## Features
* NACA 4-digit and 5-digit (standard, non-reflexed) airfoils, full-cosine point spacing
* Custom airfoil files (Selig and Lednicer formats), automatic blunt trailing-edge closing
* C-grid and rectangular (wind tunnel) domains, split into 6 four-sided blocks
* Choose which of the six split lines to export (all six are needed for mapped meshing; all six and front axis + wake axis were tested with quad-dominant + inflation), with a warning for a single line, which cannot work
* Ansys DesignModeler TXT export
* **Mesh / y⁺ assistant:** first-cell height for a target y⁺ and boundary-layer estimate, with two outputs: Ansys **Inflation** settings (first layer, growth rate, maximum layers) or a mapped-mesh **Edge Sizing** table (Number of Divisions + Bias Factor) with the expected cell count
* **Mesh quality check** (skewness, orthogonal quality, aspect ratio) against Ansys bands and Fluent limits
* **y⁺ correction** from a first Fluent result, and a **Fluent setup helper** that turns a free-stream speed and angle of attack into the inlet X/Y velocity components, the Lift/Drag vectors and the reference values, and checks Reynolds and Mach
* Turkish / English interface

## Local installation
```bash
git clone https://github.com/meceylan/AirfoilMatic.git
cd AirfoilMatic
pip install -r requirements.txt
streamlit run app.py
```
Run the tests with `pip install pytest` and `pytest`.

## Ansys workflow
1. **Import:** In DesignModeler, set `Units > Meter` first, then use `Concept > 3D Curve`, select the downloaded `.txt` file and click `Generate`.
2. **Surface:** Use `Concept > Surfaces from Edges` with the outer boundary and airfoil edges to create the flow surface.
3. **Split:** Use `Tools > Projection` with the exported split lines.
4. **Mesh:** choose one of the two workflows; the **Mesh / y⁺** tab gives the settings for both.
   * **Inflation (quad-dominant):** export the front axis + wake axis (or all six lines); a single line, or the wake axis without the front axis, makes inflation fail. Add `Inflation` on all faces with the airfoil edges **and the wake axis** as boundary, set the global Element Size to about 0.5c and enter the Edge Sizings from the table. The app keeps the trailing-edge element at least 1.5x the last inflation layer (and at least 0.003c); otherwise Ansys cannot build the inflation. Use a sharp trailing edge; blunt TE + inflation failed in our tests.
   * **Mapped:** export all six split lines (6 blocks), add `Face Meshing` (Mapped) to all faces and the `Edge Sizing` values from the table.
   * Inflation and Mapped Face Meshing cannot be combined on the same face.
5. **Check:** Confirm the cell count and check y⁺ in Fluent. Fluent reports y⁺ at the cell centroid, so expect about half the target value.

## Validation: NACA 0012
The domain and inflation mesh from the app were compared with Ladson's wind-tunnel data (NASA TM-4074, Table I: M = 0.15, Re = 2 × 10⁶, free transition, α = 4.25°).

**Setup:** c = 1 m, C-grid (R = 15 m, wake 20 m), front axis + wake axis, target y⁺ = 1. Ansys Fluent 2024 R2, Transition SST, U = 51.04 m/s, ρ = 1.225 kg/m³, μ = 3.126 × 10⁻⁵ Pa·s, inlet Tu = 1% and viscosity ratio 100. All settings were taken from the app's Mesh / y⁺ tab.

| Mesh | Elements | Max skewness | Min orth. quality | Cl | Cd |
|---|---|---|---|---|---|
| A (growth 1.15) | ~38,500 | 0.62 | 0.62 | 0.4469 | 0.00658 |
| B (growth 1.10) | 53,314 | 0.73 | 0.65 | 0.4481 | 0.00647 |
| Ladson (experiment) | | | | 0.4450 | 0.00670 |

Cl is within 1% of the experiment and Cd within 2–3.5%; the scatter between different wind tunnels for the NACA 0012 is of the same order (McCroskey, NASA TM-100019). y⁺ on the airfoil is 0.14–1.14. Residuals fully converged in 1000 iterations.

## Why split at X = 0.3c?
If the airfoil goes into DesignModeler as a single curve, or as two curves split only at the LE and TE, surface creation can produce sliver faces near the leading edge. Those faces hurt mesh quality.

AirfoilMatic cuts the airfoil vertically at **X = 0.3c** into four segments (upper-front, upper-rear, lower-front, lower-rear):
1. **Curvature isolation:** The maximum thickness of many airfoils is near 0.3c. Splitting there separates the high-curvature leading-edge region.
2. **No sliver faces:** The vertical split lines meet the outer boundaries at right angles, which avoids invalid topology at the junctions.
3. **Mapped meshing:** Every block is four-sided (in the rectangular domain the front blocks need a Side vertex). For the C-grid, the inlet arc is centered on the split line, so the arc ends exactly where the vertical lines meet the outer boundary and no short straight piece is left in front of 0.3c.

## Technology
| Component | Technology |
|---|---|
| Framework | Streamlit |
| Computation | NumPy |
| Plots | Plotly |
| Language | Python 3.11+ |

## Developer
**Muhammet Emin CEYLAN**, Iskenderun Technical University  
[LinkedIn](https://www.linkedin.com/in/muhammet-emin-ceylan-b79847334) · [GitHub](https://github.com/meceylan)

Please use the [Issues](https://github.com/meceylan/AirfoilMatic/issues) page for bugs and suggestions.

## License
MIT License. The interface font, Source Serif 4, is distributed under the SIL Open Font License 1.1 (`static/fonts/OFL-SourceSerif4.txt`).
