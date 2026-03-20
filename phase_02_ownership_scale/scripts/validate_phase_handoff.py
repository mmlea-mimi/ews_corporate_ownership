from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PHASE_1_OUTPUT_PATH = ROOT / "data/intermediate/ownership_share_filtered_parcels.csv"
PHASE_2_OUTPUT_PATH = ROOT / "outputs/ownership_scale/ownership_scale_by_parcel.csv"


def load_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing expected file: {path}")
    return pd.read_csv(path, low_memory=False)


def parcel_id_column(df: pd.DataFrame) -> str | None:
    for candidate in ["parcel_id", "situs_pID", "pID"]:
        if candidate in df.columns:
            return candidate
    return None


def summarize(df: pd.DataFrame, label: str) -> tuple[int, int | None]:
    rows = len(df)
    pid_col = parcel_id_column(df)
    unique_parcels = None

    print(f"{label} rows: {rows}")

    if pid_col is not None:
        unique_parcels = df[pid_col].astype(str).nunique(dropna=True)
        print(f"{label} unique parcels ({pid_col}): {unique_parcels}")
    else:
        print(f"{label} unique parcels: unavailable (no parcel id column found)")

    return rows, unique_parcels


def main() -> None:
    phase_1_df = load_frame(PHASE_1_OUTPUT_PATH)
    phase_1_rows, phase_1_unique = summarize(phase_1_df, "Phase 1 handoff")

    # Phase 2 starts from the exact same handoff file, so this count should match by design.
    print(f"Phase 2 starting rows: {phase_1_rows}")
    if phase_1_unique is not None:
        print(f"Phase 2 starting unique parcels: {phase_1_unique}")

    if PHASE_2_OUTPUT_PATH.exists():
        print("")
        phase_2_df = load_frame(PHASE_2_OUTPUT_PATH)
        phase_2_rows, phase_2_unique = summarize(phase_2_df, "Phase 2 parcel output")

        rows_match = phase_1_rows == phase_2_rows
        unique_match = phase_1_unique == phase_2_unique

        print("")
        print(f"Row count match: {rows_match}")
        if phase_1_unique is not None and phase_2_unique is not None:
            print(f"Unique parcel count match: {unique_match}")
    else:
        print("")
        print("Phase 2 parcel output not found yet. Run ownership_scale.py first to compare outputs.")


if __name__ == "__main__":
    main()
