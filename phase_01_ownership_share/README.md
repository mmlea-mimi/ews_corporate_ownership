# Phase 1: Ownership Share

This folder contains the first phase of the pipeline: identifying the parcels that should move forward into ownership-scale analysis.

## Role in pipeline

- Input: shared source data in `data/raw/`
- Main output: filtered parcel handoff in `data/intermediate/ownership_share_filtered_parcels.csv`
- Supporting outputs: summaries in `outputs/ownership_share/`

## Active script

- `scripts/00_ingest_targets.R`

This phase should remain the R-based workflow where parcel filtering and spatial logic live.
