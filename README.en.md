# AirfoilMatic V0.6.6 Beta — 2D CFD Domain Generator

[Türkçe](README.md) | **English**

**[Run AirfoilMatic in your browser](https://airfoilmatic.streamlit.app/)**

AirfoilMatic builds the geometry of a 2D CFD flow domain around an airfoil (NACA 4/5-digit, one of 300 sections selected from the UIUC database, or a custom `.dat` file) and exports it in the Ansys DesignModeler `3D Curve` text format. The domain is already split into six four-sided blocks, so Ansys Meshing can produce a structured (mapped) mesh. It also gives you matching mesh settings (Inflation, Edge Sizing) and Fluent setup values.

## Features
* NACA 4-digit and 5-digit (standard, non-reflexed) airfoils, drawn from the NACA equations with 201 points and full-cosine spacing
* **Section search and random section:** 300 sections selected from the UIUC Airfoil Coordinates Database (NACA 6 and 16 series, NASA SC(2)/NLF/LS, Eppler, Selig, Wortmann, Hepperle, Drela, RAE, Delft DU and more). Type a name (`63-215`, `e387`, `clark y`); the 🎲 button picks a random section filtered by thickness, camber and family, and back/forward return to earlier ones. The app does not invent sections: a name that is not listed is reported as not in the database
* Custom airfoil files (`.dat`, `.txt`, `.csv`; Selig and Lednicer formats), automatic blunt trailing-edge closing. Units, origin and point order do not matter: the profile is moved so its leading edge is at the origin and scaled to the chord. Decimal commas, `;` separators, touching Fortran columns, a point-number column or a constant third column are read too. A profile drawn backwards is mirrored; tilted, very coarse or broken files get a message
* **Use-as-drawn mode:** the closed outline of an uploaded file is used in its own point order, so shapes that go back in x (a vortex generator, a flap, a kinked section) are kept (inflation workflow only: front axis + wake axis)
* C-grid and rectangular (wind tunnel) domains, split into 6 four-sided blocks; domain sizes are entered in chords
* Choose which of the six split lines to export (all six are needed for mapped meshing; all six and front axis + wake axis were tested with quad-dominant + inflation), with a warning for a single line, which cannot work
* Domain export: Ansys DesignModeler TXT and SpaceClaim TXT (the SpaceClaim format is not tried yet)
* **Profile only:** upper and lower surface without a domain; DesignModeler TXT, SolidWorks ZIP (two files for Curve Through XYZ Points) and SpaceClaim TXT
* **m / mm** output unit in the sidebar (all downloaded files)
* Flow input: Reynolds, **Mach + Reynolds + temperature** (with the pressure-far-field values; Sutherland viscosity) or speed + density + viscosity
* **Mesh / y⁺ assistant:** first-cell height for a target y⁺ and boundary-layer estimate, with two outputs: Ansys **Inflation** settings (first layer, growth rate, maximum layers) or a mapped-mesh **Edge Sizing** table (Number of Divisions + Bias Factor) with the expected cell count
* **Mesh quality check** (skewness, orthogonal quality, aspect ratio) against Ansys bands and Fluent limits
* **y⁺ correction** from a first Fluent result, and a **Fluent setup helper** that turns a free-stream speed and angle of attack into the inlet X/Y velocity components, the Lift/Drag vectors and the reference values, and checks Reynolds and Mach (speed of sound from the temperature); **free-stream turbulence decay** (SST) from the inlet to the airfoil
* **Automation tab:** an **angle-of-attack sweep** (CSV; even steps or your own list of angles, e.g. 1.3, 2.8, 6.8) for a polar, the Fluent journal and the **polar** from the report file (mean and range of the last N iterations per angle, oscillating / short angles flagged, Cl–α, Cd–α and Cl–Cd charts, CSV; tried with the Fluent 2024 R2 report file format)
* **Fluent journal:** a TUI journal (`.jou`) that steps a named expression `aoa` through the angles of the sweep and runs the iterations (the case uses `aoa` in the pressure-far-field flow direction or the velocity-inlet components and in the Cl/Cd expression reports; the app prints these expressions and the `clconv` stop criterion for the angle where Cl ≈ 0). Case & data can be saved every k angles (the last angle always); a stopped sweep continues from the last save (first iteration by hand, Yes to Fluent's new-file question; the polar tool reads both report files). Tried in Ansys Fluent 2024 R2 (standalone) with a 3-angle sweep (50 iterations each) and an 11-angle sweep (−4…16°, with Convergence Conditions, velocity-inlet case) and a sweep with a pressure-far-field case (M 0.3, 2…8°); continuing a stopped sweep was tried too; Workbench and case overwriting have not been tried yet
* Turkish / English interface

## Local installation
```bash
git clone https://github.com/meceylan/AirfoilMatic.git
cd AirfoilMatic
pip install -r requirements.txt
streamlit run app.py
```
Run the tests with `pip install pytest` and `pytest`. `tests/test_app.py` runs the app itself headless (Streamlit AppTest); `tests/test_hard_files.py` reads 75 hard files written from a known profile and compares the result with the true outline; `tests/test_database_findings.py` covers the problems found by running the whole UIUC database (overlapping surfaces); `tests/test_library.py` checks that every section in the selection builds a clean domain, and the search.

## Ansys workflow
1. **Import:** In DesignModeler, first set `Units` to the output unit chosen in the sidebar (`Meter` for m, `Millimeter` for mm), then use `Concept > 3D Curve`, select the downloaded `.txt` file and click `Generate`.
2. **Surface:** Use `Concept > Surfaces from Edges` with the outer boundary and airfoil edges to create the flow surface.
3. **Split:** Use `Tools > Projection` with the exported split lines.
4. **Mesh:** choose one of the two workflows; the **Mesh / y⁺** tab gives the settings for both.
   * **Inflation (quad-dominant):** export the front axis + wake axis (or all six lines); a single line, or the wake axis without the front axis, makes inflation fail. Add `Inflation` on all faces with the airfoil edges **and the wake axis** as boundary, set the global Element Size to about 0.5c and enter the Edge Sizings from the table. The app keeps the trailing-edge element at least 1.5x the last inflation layer (and at least 0.003c); otherwise Ansys cannot build the inflation. Use a sharp trailing edge; blunt TE + inflation failed in our tests.
   * **Mapped:** export all six split lines (6 blocks), add `Face Meshing` (Mapped) to all faces and the `Edge Sizing` values from the table.
   * Inflation and Mapped Face Meshing cannot be combined on the same face.
5. **Check:** Confirm the cell count and check y⁺ in Fluent. Fluent reports y⁺ at the cell centroid, so expect about half the target value.

## Comparison with NACA 0012 data
The domain and inflation mesh from the app were compared with Ladson's wind-tunnel data (NASA TM-4074, Table I: M = 0.15, Re = 2 × 10⁶, free transition, α = 4.25°).

**Setup:** c = 1 m, C-grid (R = 15 m, wake 20 m), front axis + wake axis, target y⁺ = 1. Ansys Fluent 2024 R2, Transition SST, U = 51.04 m/s, ρ = 1.225 kg/m³, μ = 3.126 × 10⁻⁵ Pa·s, inlet Tu = 1% and viscosity ratio 100. All settings were taken from the app's Mesh / y⁺ tab.

| Mesh | Elements | Max skewness | Min orth. quality | Cl | Cd |
|---|---|---|---|---|---|
| A (growth 1.15) | ~38,500 | 0.62 | 0.62 | 0.4469 | 0.00658 |
| B (growth 1.10) | 53,314 | 0.73 | 0.65 | 0.4481 | 0.00647 |
| Ladson (experiment) | | | | 0.4450 | 0.00670 |

Cl is within 1% of the experiment and Cd within 2–3.5%; the scatter between different wind tunnels for the NACA 0012 is of the same order (McCroskey, NASA TM-100019). y⁺ on the airfoil is 0.14–1.14. Residuals fully converged in 1000 iterations.

**Limits:** Only one section, one angle, one Reynolds number and the inflation mesh were tried; there is no result for the mapped mesh. The turbulence level of Ladson's tunnel is not known and a viscosity ratio of 100 was chosen at the inlet (about 0.43% Tu reaches the leading edge); how close Cd is to the experiment may depend partly on that choice. Read the result as "consistent with the experiment", not as a firm validation.

## Scope
* The mesh plan is built for low speed (Mach < 0.3). The Mach input accepts up to 1.0 and suggests a pressure far field above Mach 0.3, but gives no mesh settings specific to compressible flow. In Fluent 2024 R2 (NACA 0012, 15c C-grid) a pressure far field did not converge at M 0.15 at a non-zero angle, and converged cleanly at M 0.3 and 0.5 (whole outer boundary far-field, Time Scale Factor 0.2); use a velocity inlet at low Mach. Transonic sections in the library such as RAE and NASA SC(2) get the same plan, but there is no separate route for the shock region.
* Domain size (default 15c): at high Cl the far-field boundary affects the lift. As Cl grows, enlarge the radius and check that the result does not change.

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

The coordinates in the section selection come from the [UIUC Airfoil Coordinates Database](https://m-selig.ae.illinois.edu/ads/coord_database.html) maintained by Prof. Michael S. Selig and are not covered by the app's MIT license. The selection can be rebuilt from the database with `tools/build_airfoil_library.py`.
