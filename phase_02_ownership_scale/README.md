# Phase 2: Ownership Scale

This folder contains the second phase of the pipeline: exact-match ownership-scale analysis on the filtered parcel dataset from phase 1.

## Role in pipeline

- Input: `data/intermediate/ownership_share_filtered_parcels.csv`
- Outputs:
  - `outputs/ownership_scale/ownership_scale_by_parcel.csv`
  - `phase_02_ownership_scale/excel/ownership_scale_by_parcel.xlsx`
  - `phase_02_ownership_scale/excel/ownership_scale_by_owner.xlsx`
  - other ownership-scale Excel files in `phase_02_ownership_scale/excel/`

## Active script

- `scripts/ownership_scale.py`
- `scripts/validate_phase_handoff.py`

This phase should remain the Python-based workflow where owner name/address cleaning and exact-match grouping live.

## Count continuity

Phase 2 reads the exact phase 1 handoff file at `data/intermediate/ownership_share_filtered_parcels.csv`, so the starting number of likely-corporate-owned parcel rows should match the final phase 1 handoff count directly.

To check this quickly:

```bash
python3 phase_02_ownership_scale/scripts/validate_phase_handoff.py
```
