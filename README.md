# Corporate Ownership Pipeline

This repository keeps one parent folder and splits the active workflow into two clear phases:

`TCAD raw data -> phase 1: ownership share (R) -> filtered parcel dataset -> phase 2: ownership scale (Python)`

The goal is still simplicity. R remains the spatial filtering stage. Python remains the ownership-scale stage.

## Project structure

```text
phase_01_ownership_share/
  scripts/         R scripts for parcel selection / filtering
  excel/           Excel inputs/reference files for ownership share
phase_02_ownership_scale/
  scripts/         Python scripts for owner grouping / scale analysis
  excel/           Excel outputs/reference files for ownership scale
data/
  raw/             source files from TCAD and other inputs
  intermediate/    handoff files between the two phases
outputs/
  ownership_share/ phase 1 summaries
  ownership_scale/ phase 2 outputs
docs/              short method notes
```

## Phase handoff

The shared handoff file between phases lives at:

`data/intermediate/ownership_share_filtered_parcels.csv`

Phase 1 writes that file. Phase 2 reads that file.

## Standard parcel-level column names

Keep these names consistent across both phases wherever possible:

- `parcel_id`
- `owner_name`
- `owner_address`
- `situs_address`
- `situs_lat`
- `situs_long`

The Python phase only requires `owner_name` and `owner_address`, but the full set keeps the handoff easier to inspect, map, and join back to parcel-level data.

## Naming conventions

- Shared raw data: `data/raw/`
- Phase 1 Excel files: `phase_01_ownership_share/excel/`
- Shared handoff file: `data/intermediate/ownership_share_filtered_parcels.csv`
- Phase 1 summary output: `outputs/ownership_share/`
- Phase 2 parcel-level output: `outputs/ownership_scale/ownership_scale_by_parcel.csv`
- Phase 2 Excel files: `phase_02_ownership_scale/excel/`
- Phase 2 parcel-level Excel output: `phase_02_ownership_scale/excel/ownership_scale_by_parcel.xlsx`
- Phase 2 owner-level output: `phase_02_ownership_scale/excel/ownership_scale_by_owner.xlsx`

## How to run

Run phase 1 first, then phase 2:

```bash
Rscript phase_01_ownership_share/scripts/00_ingest_targets.R
python3 phase_02_ownership_scale/scripts/ownership_scale.py
python3 phase_02_ownership_scale/scripts/validate_phase_handoff.py
```

## Note

The existing `ownership_scale/` folder is left in place as a legacy standalone copy and remains ignored by git.
