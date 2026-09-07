# Navigation Smoke Visualization

This folder provides a small browser-based visualization for the PRMS closed-loop navigation smoke test.

## Files

- `index.html`: self-contained trajectory viewer.
- `trace_sample.json`: sample trace exported from a successful smoke run.
- `greenhouse_reference.png`: browser-friendly rendering of the reference occupancy map.

## Generate a fresh trace

From the repository root on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_wsl_closed_loop_nav_smoke.ps1
```

The script writes a fresh trace to:

```text
outputs/nav_smoke/latest_trace.json
```

Open `index.html` in a browser and use **Load trace JSON** to inspect the generated trace.
