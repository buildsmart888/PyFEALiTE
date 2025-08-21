# TODOs — PyNite Plugin (Phase 2)

Goal: เพิ่ม 3D analysis capabilities ผ่าน PyNite plugin
Owner: PyFEALiTE core team
Start: Week 3
Duration: Weeks 3–6

---

## High-level checklist (user request)
- [ ] Run comprehensive testing of new plugin framework
  - [ ] Test plugin system imports and basic functionality
  - [ ] Test enhanced structure with plugin support
  - [ ] Run demo script and validate outputs


## Phase 2 — PyNite Plugin Plan (Weeks 3–6)

Week 3 — Data & API adapters
- [ ] Data Conversion: Implement converters between PyFEALiTE and PyNite data models
  - [ ] Node mapping (2D→3D/3D→2D)
  - [ ] Element mapping (FrameElement2D ↔ PyNite members)
  - [ ] Loads mapping (NodalLoad, PointLoad, UniformLoad)
  - [ ] Section & Material mapping (Rectangular, IPE, isotropic materials)
- [ ] API adapter: Simple facade to run PyNite analysis using PyFEALiTE structures

Week 4 — 3D Static Analysis & P-Delta
- [ ] Implement Static 3D analysis via PyNite plugin
- [ ] Implement P-Delta analysis wrapper and iterative solver interface
- [ ] Unit tests: Compare PyFEALiTE 2D uplift/slice cases vs PyNite 3D projection
- [ ] Example: 3D portal static loadcase demo

Week 5 — Buckling & Modal
- [ ] Buckling (Eigenvalue) analysis wrapper to PyNite
- [ ] Modal analysis adapter and basic mode shapes export
- [ ] Integration tests against known analytical solutions
- [ ] Example: Simple column buckling validation

Week 6 — Integration, Validation & Docs
- [ ] Integration Testing: Validate PyNite plugin against reference problems
  - [ ] 3D portal validation (compare with hand calc / references)
  - [ ] Multi-span beam validation
- [ ] Documentation: Usage examples and API docs (README + Sphinx docs)
- [ ] Demo script: `examples/pynite_3d_demo.py` with reproducible outputs
- [ ] Finalize unit tests and CI hooks

---

## Acceptance Criteria
- [ ] Converters reliably translate structure, loads, and sections (round-trip tests)
- [ ] Plugin runs PyNite static 3D and returns nodal displacements and element forces
- [ ] P-Delta wrapper converges and matches reference results within tolerance
- [ ] Buckling/modal wrappers return eigenvalues and mode shapes comparable to references
- [ ] Example demo produces committed PNGs and text summary in `demo_exports/pynite_3d_demo/`
- [ ] CI runs for plugin tests added to `.github/workflows/ci.yml`

## Notes and assumptions
- Assume PyNite is available as `pynite` PyPI package (if not, add installation step)
- Keep conversions unit-consistent (SI: N, m, rad)
- Minimize invasive changes to core PyFEALiTE — plugin should be isolated under `pyfealite.plugins.pynite`

## Quick start tasks (developer)
1. Create `pyfealite.plugins.pynite` package skeleton
2. Implement `converters.py` with Node/Element/Load mapping
3. Implement `adapter.py` to expose `run_pynite_static(structure, load_case)`
4. Add tests under `tests/test_plugins/test_pynite_plugin.py`
5. Add `examples/pynite_3d_demo.py` with deterministic geometry and loads

---

Last updated: 2025-08-21
Updated by: automation-agent
