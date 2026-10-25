# AirfoilMatic V0.4.1 Beta — 2D CFD Domain Generator

[Türkçe](README.md) | **English**

**[Run AirfoilMatic in your browser](https://airfoilmatic-gkxdkjpsclawjnbhmzng89.streamlit.app/)**

AirfoilMatic builds the geometry of a 2D CFD flow domain around an airfoil (NACA 4/5-digit or a custom `.dat` file) and exports it in the Ansys DesignModeler `3D Curve` text format. The domain is already split into six four-sided blocks, so Ansys Meshing can produce a structured (mapped) mesh. It also gives you the matching Edge Sizing settings and a grid-independence (GCI) calculator.

## Features
* NACA 4-digit and 5-digit (standard, non-reflexed) airfoils, full-cosine point spacing
* Custom airfoil files (Selig and Lednicer formats), automatic blunt trailing-edge closing
* C-grid and rectangular (wind tunnel) domains, split into 6 four-sided blocks
* Choose which of the six split lines to export (all six are needed for mapped meshing; all six and front axis + wake axis were tested with quad-dominant + inflation), with a warning for a single line, which cannot work
* Ansys DesignModeler TXT export
* **Mesh / y⁺ assistant:** first-cell height for a target y⁺ and boundary-layer estimate, with two outputs: Ansys **Inflation** settings (first layer, growth rate, maximum layers) or a mapped-mesh **Edge Sizing** table (Number of Divisions + Bias Factor) with the expected cell count
* **Mesh quality check** (skewness, orthogonal quality, aspect ratio) against Ansys bands and Fluent limits
* **y⁺ correction** from a first Fluent result, and a **Fluent setup helper** that turns a free-stream speed and angle of attack into the inlet X/Y velocity components, the Lift/Drag vectors and the reference values, and checks Reynolds and Mach
* **Grid independence:** Grid Convergence Index calculator (Celik et al., 2008) with a Cl/Cd convergence plot, plus an optional suggested grid family
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
   * **Inflation (quad-dominant):** export all six lines or the front axis + wake axis (the tested selections; a single line stays as a slit inside one face and fails). Add `Inflation` on all faces with the airfoil edges as boundary (the wake axis optionally too), set the global Element Size to about 0.5c, and add the Edge Sizings from the table with Behavior = Soft (Hard is not supported on inflated edges). Keep the trailing-edge element at about 0.003c or larger: in our Ansys 2024 R2 tests (c = 1 m) about 1 mm failed and about 3 mm worked. Use a sharp trailing edge; blunt TE + inflation failed in our tests. Check that Bounding Box Diagonal is tens of meters before meshing.
   * **Mapped:** export all six split lines (6 blocks), add `Face Meshing` (Mapped) to all faces and the `Edge Sizing` values from the table.
   * Inflation and Mapped Face Meshing cannot be combined on the same face.
5. **Check:** Confirm the cell count and check y⁺ in Fluent. Fluent reports y⁺ at the cell centroid, so expect about half the target value.

## Grid independence (GCI)
The cell count alone does not tell you whether a mesh is good enough. Results must be shown to change little when the grid is refined. The **Grid Independence** tab:
1. takes the cell counts and Cl/Cd results of your three Fluent runs,
2. reports the apparent order *p*, the extrapolated value, and GCI_fine, following Celik et al. (2008), and warns about oscillatory or divergent behavior,
3. plots Cl and Cd against h = 1/√N with the Richardson fit and the extrapolated value,
4. optionally suggests a consistent grid family (refinement ratio √2 per direction by default, about 2× cells per level).

Reference: Celik, I. B., Ghia, U., Roache, P. J., Freitas, C. J., Coleman, H., Raad, P. E., *Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications*, J. Fluids Eng. 130(7), 078001, 2008.

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

## License
MIT License.
