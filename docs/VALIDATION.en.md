# AirfoilMatic — Ansys / Fluent runs

[Türkçe](VALIDATION.md) | **English** · [Back to the README](../README.en.md)

This page collects how the app's outputs were tried in Ansys / Fluent. Anything not marked "tried" here should not be taken as tried. All Fluent runs were made with Ansys Fluent 2024 R2.

## Contents
- [Not tried yet](#not-tried-yet)
- [The app's Fluent mesh file (.msh)](#the-apps-fluent-mesh-file-msh)
- [Comparison with NACA 0012 data](#comparison-with-naca-0012-data)
- [NACA 4412: mapped mesh and use-as-drawn mode](#naca-4412-mapped-mesh-and-use-as-drawn-mode)
- [Mesh independence (GCI)](#mesh-independence-gci)
- [Fluent journal and angle sweep](#fluent-journal-and-angle-sweep)
- [Other outputs](#other-outputs)
- [Scope](#scope)
- [Why split at X = 0.3c?](#why-split-at-x--03c)

## Not tried yet
* Case overwriting in the journal has not been tried yet.
* The section-only DesignModeler TXT has not been tried yet (the domain TXT was).
* The journal was tried inside Workbench and does not work there (a "Settings have changed" question at every angle change, asked again even with "current and future calculations"); use standalone Fluent.

## The app's Fluent mesh file (.msh)
With Mapped selected the app builds the mesh of the C-grid or rectangular domain itself: 6 blocks with the divisions and bias factors of the Edge Sizing table, filled by transfinite interpolation; boundaries already named `inlet`, `outlet`, `wall`. No DesignModeler or Meshing needed: File → Read → Mesh in Fluent. The cell count and quality (skewness, orthogonal quality) are shown in the app; the file is limited to 1 000 000 cells.

**How the mesh is built**
* On the front blocks the grid lines leave the wall at right angles: for NACA 4412 max skewness 0.37, minimum orthogonal quality 0.84 (the mesh Ansys made from the same table: skewness 0.45); tried in Fluent 2024 R2: the minimum orthogonal quality is 0.845 in Fluent too, and Cl at −4…8° is the same as on the earlier mesh (8°: 1.22287 / before 1.22338), Cd within 0.2 %. This fixes the squeezed cells behind the nose of strongly cambered sections (S9104 at the nose: skewness 0.90 → 0.64, orthogonal quality 0.05 → 0.54; the worst cell of the whole mesh is now at the trailing edge, 0.73 / 0.41).
* The front axis leaves the leading edge along the wall normal and bends to horizontal within one chord (for the leading-edge corner at high Re). Tried in Fluent 2024 R2: NACA 4412 minimum orthogonal quality 0.895, Cl at −4…8° the same as on the earlier mesh (8°: 1.22288).
* The mesh has vertical columns above and below the rear part (for the thin far-field cells of strongly cambered sections); they were in the mesh of the bent-axis NACA 4412 run, so they were tried with it.

**First runs (earlier mesh: max skewness 0.52, orthogonal quality 0.493)**
* Fluent 2024 R2 read the file and passed Mesh Check without errors; minimum orthogonal quality 0.493 (the same as the app computes).
* Solved for NACA 4412 at −4…8° (SST k-ω, Re 2 × 10⁶): Cl and Cd match the Ansys mesh within 0.01 % / 0.05 % (0°: Cl 0.41739 on both).
* A UIUC section with a blunt trailing edge, GA(W)-1 (LS(1)-0417), was solved the same way: 91 122 cells, −4…8° converged without a question, zero-lift angle −3.87° (thin-airfoil theory −4.27°).

**Rectangular domain:** tried in Fluent 2024 R2: NACA 4412 at −4…8°, Cl within 0.2 % of the C-grid, 8°: 1.22537; Cd 1.6 % lower at 8°, most likely from the domain shape (not tested further).

## Comparison with NACA 0012 data
The domain and inflation mesh from the app were compared with Ladson's wind-tunnel data (NASA TM-4074, Table I: M = 0.15, Re = 2 × 10⁶, free transition, α = 4.25°).

**Setup:** c = 1 m, C-grid (R = 15 m, wake 20 m), front axis + wake axis, target y⁺ = 1. Ansys Fluent 2024 R2, Transition SST, U = 51.04 m/s, ρ = 1.225 kg/m³, μ = 3.126 × 10⁻⁵ Pa·s, inlet Tu = 1% and viscosity ratio 100. All settings were taken from the app's Mesh / y⁺ tab.

| Mesh | Elements | Max skewness | Min orth. quality | Cl | Cd |
|---|---|---|---|---|---|
| A (growth 1.15) | ~38,500 | 0.62 | 0.62 | 0.4469 | 0.00658 |
| B (growth 1.10) | 53,314 | 0.73 | 0.65 | 0.4481 | 0.00647 |
| Ladson (experiment) | | | | 0.4450 | 0.00670 |

Cl is within 1% of the experiment and Cd within 2–3.5%; the scatter between different wind tunnels for the NACA 0012 is of the same order (McCroskey, NASA TM-100019). y⁺ on the airfoil is 0.14–1.14. Residuals fully converged in 1000 iterations.

**Limits:** This comparison used one section, one angle and one Reynolds number. The turbulence level of Ladson's tunnel is not known and a viscosity ratio of 100 was chosen at the inlet (about 0.43% Tu reaches the leading edge); how close Cd is to the experiment may depend partly on that choice. Read the result as "consistent with the experiment", not as a firm validation.

**Angle sweep and stall (SST k-ω, 2026-11):** The same mesh (B) and velocity-inlet case with fully turbulent SST k-ω were compared with Ladson's Table IX (No. 80 grit, transition fixed at 0.05c, Re 2 × 10⁶) at the same angles (the app's journal with its own list of angles). At 0° Cd is 2 % from the experiment; from 0 to 15° Cl is 2–3.5 % above it (Ladson writes that theory gives a lift-curve slope up to 7 % above the experiment and that the data carry a 2 % tunnel correction); from 6 to 14° Cd is 7–19 % high. In the experiment stall comes between 15 and 16°. SST gave attached flow at 16.02° (Cl 1.45; experiment 1.07), and at 16.99° URANS (Δt = 0.01 c/U, 3000 steps) also settled to attached flow (Cl 1.46, Cd 0.045; experiment 1.09 / 0.249). The oscillation of the steady solver at this angle (Cl 0.30–1.35) was not physical. So SST gives the stall angle and Cl_max too high; an oscillating steady solution is not always stall, check it with URANS. With Transition SST the steady sweep oscillated above 8°.

## NACA 4412: mapped mesh and use-as-drawn mode
2026-11. The cambered section was built along two independent paths and solved with the same Fluent setup (SST k-ω, Re 2 × 10⁶, velocity inlet, the app's journal) at −4, 0, 4 and 8°: (1) from the section search, a 6-block **mapped mesh** (84 501 quads; the app estimated 84 870; max skewness 0.445); (2) from a Selig `.dat` file, the **use-as-drawn mode** with inflation (47 674 elements; max skewness 0.658). The setup was moved to the second mesh with `/mesh/replace`. The two paths agree within 1.5 % in Cl and 2 % in Cd; the zero-lift angle is −3.90° and −3.98° (thin-airfoil theory −4.15°, experiment ≈ −4°). The mapped mesh used one common bias on the wall-normal edges (changes the first cell by at most 2 %).

## Mesh independence (GCI)
Coarse / medium / fine Fluent meshes from the same inputs (cell sizes by √2; about 2x the cells per step; the medium mesh is the one shown in the app). GCI by Celik et al. 2008 (J. Fluids Eng. 130, 078001); same result as Celik's example. Tried in Fluent 2024 R2 with NACA 4412 at 4°: Cl 0.8355 / 0.8359 / 0.8353 (coarse / medium / fine), Cd within 0.1 %; the default mesh is mesh independent for this flow.

## Fluent journal and angle sweep
* Tried in Ansys Fluent 2024 R2 (standalone) with a 3-angle sweep (50 iterations each), an 11-angle sweep (−4…16°, with Convergence Conditions, velocity-inlet case) and a sweep with a pressure-far-field case (M 0.3, 2…8°); continuing a stopped sweep was tried too.
* Own list of angles tried with 1.99, 4.01, 6.11, 8.08.
* The polar tool was tried with the Fluent 2024 R2 report file format.
* Tried inside Workbench, where it does not work; case overwriting has not been tried yet.

## Other outputs
* DesignModeler TXT and SpaceClaim TXT: both tried by users; the SolidWorks section output too.
* Use-as-drawn mode (inflation workflow only: front axis + wake axis): tried with NACA 4412 in Fluent 2024 R2.
* Split lines: all six are needed for mapped meshing; all six and front axis + wake axis were tested with quad-dominant + inflation.
* Moving a set-up case to a new mesh with `/mesh/replace`: tried in Fluent 2024 R2.

## Scope
* The mesh plan is built for low speed (Mach < 0.3). The Mach input accepts up to 1.0 and suggests a pressure far field above Mach 0.3, but gives no mesh settings specific to compressible flow. In Fluent 2024 R2 (NACA 0012, 15c C-grid) a pressure far field did not converge at M 0.15 at a non-zero angle, and converged cleanly at M 0.3 and 0.5 (whole outer boundary far-field, Time Scale Factor 0.2); use a velocity inlet at low Mach. Transonic sections in the library such as RAE and NASA SC(2) get the same plan, but there is no separate route for the shock region.
* Domain size (default 15c): at high Cl the far-field boundary affects the lift. As Cl grows, enlarge the radius and check that the result does not change.

## Why split at X = 0.3c?
If the airfoil goes into DesignModeler as a single curve, or as two curves split only at the LE and TE, surface creation can produce sliver faces near the leading edge. Those faces hurt mesh quality. AirfoilMatic cuts the airfoil vertically at **X = 0.3c** into four segments (upper-front, upper-rear, lower-front, lower-rear):
1. **Curvature isolation:** The maximum thickness of many airfoils is near 0.3c. Splitting there separates the high-curvature leading-edge region.
2. **No sliver faces:** The vertical split lines meet the outer boundaries at right angles, which avoids invalid topology at the junctions.
3. **Mapped meshing:** Every block is four-sided (in the rectangular domain the front blocks need a Side vertex). For the C-grid, the inlet arc is centered on the split line, so the arc ends exactly where the vertical lines meet the outer boundary and no short straight piece is left in front of 0.3c.
