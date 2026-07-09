# Dynamic Foraging — QC Capsule

Runs quality control for a [dynamic foraging](https://github.com/AllenNeuralDynamics/Aind.Behavior.DynamicForaging)
session. The capsule runs the raw (contract QC) stage over the raw acquisition and
the processed (behavior) stage over the trials, licks, and rewards data packaged in the NWB file. The output is a combined
`aind-data-schema` `quality_control.json` plus the supporting reference media.

> **Note:** Data must be acquired in the `aind-behavior-dynamic-foraging` data
> contract format to be compatible with this capsule.

Uses functions from the dynamic foraging processing [library](https://github.com/AllenNeuralDynamics/dynamic-foraging-processing)
## Input
Two assets are mounted under `/data` — **both are required**:

- **The raw acquisition directory** (data-contract format: Harp registers, software
  events, ...) — the raw stage QC's the data contract on the `RawDataLoader` object.
- **The NWB file** (`behavior.nwb.zarr`) produced by the [NWB packaging capsule](https://github.com/AllenNeuralDynamics/dynamic_foraging_nwb_packaging_capsule) — the trials table is extracted from the NWB file as a `pandas.DataFrame` and the lick/reward times are extarcted as `numpy arrays` and are QC'd and added to the processed QC stage. 

```
/data/
├── <acquisition_asset>/      # raw acquisition directory
│   └── behavior/ ...
└── <nwb_asset>/
    └── behavior.nwb.zarr     # from the NWB capsule
```

## Output
Written to `/results`:

| Path | Description |
| --- | --- |
| `quality_control.json` | `aind-data-schema` `QualityControl` combining the raw and processed metrics. |
| `qc/` | Supporting figures the metrics reference (`side_bias.png`, `lick_intervals.png`). |

The QC combines:

- **Raw (contract QC)** — Harp devices, cameras, CSV streams, the data contract,
  and task-specific checks (run over the raw acquisition).
- **Processed (behavior)** — side bias and lick-interval metrics computed from the
  NWB `trials` table and lick times.

## How it works
The capsule is a thin wrapper over `dynamic_foraging_processing.pipeline.Pipeline`.
It builds a loader for the raw acquisition (raw QC) and reads the NWB file, then
**passes the in-memory `NWBFile` into `run_qc`** (which supplies the processed-QC
inputs):

```python
from pathlib import Path

from hdmf_zarr.nwb import NWBZarrIO

from dynamic_foraging_processing.pipeline import Pipeline
from dynamic_foraging_processing.raw_data_loader import RawDataLoader

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")

# Resolve the two input assets under /data.
acquisition_dir = ...          # the raw acquisition directory
nwb_path = ...                 # <nwb_asset>/behavior.nwb.zarr

loader = RawDataLoader(path=acquisition_dir)

# run_qc reads the trials table and lick times off the NWB file, so keep the
# store open (its Zarr datasets are lazy) while it runs.
with NWBZarrIO(str(nwb_path), mode="r") as io:
    nwb_file = io.read()
    Pipeline(loader).run_qc(nwb_file, RESULTS_DIR)
```

`run_qc(nwb_file, output_path)` writes `RESULTS_DIR / "quality_control.json"` and
the figure assets into `RESULTS_DIR / "qc"` (override the subfolder with
`run_qc(nwb_file, RESULTS_DIR, folder_directory="...")`). The metric references are
stored relative to `quality_control.json` (e.g. `qc/side_bias.png`) so the QC
portal resolves them.

## Environment
`Pipeline` imports both the NWB and QC modules, so install the `full` extra
(`qc` + `nwb`):

```bash
pip install "dynamic-foraging-processing[full] @ git+https://github.com/AllenNeuralDynamics/dynamic-foraging-processing.git"
```
