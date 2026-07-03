# Dynamic Foraging — QC Capsule

Runs quality control over a raw [dynamic foraging](https://github.com/AllenNeuralDynamics/Aind.Behavior.DynamicForaging)
acquisition. The capsule loads the raw acquisition through the
data contract, runs the raw (contract QA) and processed (behavior) QC stages, and
writes an `aind-data-schema` `quality_control.json` plus the supporting figures.

> **Note:** Data must be acquired in the `aind-behavior-dynamic-foraging` data
> contract format to be compatible with this capsule.

## Input
A single raw acquisition directory mounted under `/data`, in the data-contract
format (Harp device registers, software events, camera data, and the task-logic /
rig / session input schemas).

```
/data/
└── <asset_name>/            # the acquisition directory
    ├── acquisition.json
    ├── ...
    └── behavior/            # Harp registers, software events, ...
```

## Output
Written to `/results`:

| Path | Description |
| --- | --- |
| `quality_control.json` | `aind-data-schema` `QualityControl` combining the raw and processed metrics. |
| `dynamic-foraging-qc/` | Supporting figures the metrics reference (`side_bias.png`, `lick_intervals.png`). |

The QC combines:

- **Raw (contract QA)** — Harp devices, cameras, CSV streams, the data contract,
  and task-specific checks.
- **Processed (behavior)** — side bias and lick-interval metrics computed from the
  `trials` table and lick times.

## How it works
The capsule is a thin wrapper over `dynamic_foraging_processing.pipeline.Pipeline`:

```python
from pathlib import Path

from dynamic_foraging_processing.pipeline import Pipeline
from dynamic_foraging_processing.raw_data_loader import RawDataLoader

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")

# The acquisition directory is the single dataset mounted under /data.
acquisition_dir = next(path for path in DATA_DIR.iterdir() if path.is_dir())

loader = RawDataLoader(path=acquisition_dir)
Pipeline(loader).run_qc(RESULTS_DIR)
```

`run_qc` writes `RESULTS_DIR / "quality_control.json"` and the figure assets into
`RESULTS_DIR / "qc"` (override the subfolder with `run_qc(RESULTS_DIR, folder_directory="...")`).
The metric references are stored relative to `quality_control.json` (e.g.
`qc/side_bias.png`) so the QC portal resolves them.

## Environment
`Pipeline` imports both the NWB and QC modules, so install the `full` extra
(`qc` + `nwb`):

```bash
pip install "dynamic-foraging-processing[full] @ git+https://github.com/AllenNeuralDynamics/dynamic-foraging-processing.git"
```

