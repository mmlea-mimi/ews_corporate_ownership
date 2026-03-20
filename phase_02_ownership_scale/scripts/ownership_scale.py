from pathlib import Path
import math

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data/intermediate/ownership_share_filtered_parcels.csv"
PARCEL_OUTPUT_PATH = ROOT / "outputs/ownership_scale/ownership_scale_by_parcel.csv"
PARCEL_OUTPUT_XLSX_PATH = ROOT / "phase_02_ownership_scale/excel/ownership_scale_by_parcel.xlsx"
OWNER_OUTPUT_PATH = ROOT / "phase_02_ownership_scale/excel/ownership_scale_by_owner.xlsx"

# The Python step only requires owner_name and owner_address to compute the
# exact-match baseline, but we standardize a few common parcel columns here so
# the R -> Python handoff stays consistent.
COLUMN_ALIASES = {
    "parcel_id": ["parcel_id", "situs_pID", "pID"],
    "owner_name": ["owner_name"],
    "owner_address": ["owner_address"],
    "situs_address": ["situs_address"],
    "situs_lat": ["situs_lat"],
    "situs_long": ["situs_long"],
}

REQUIRED_COLUMNS = ["owner_name", "owner_address"]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}

    for standard_name, aliases in COLUMN_ALIASES.items():
        if standard_name in df.columns:
            continue

        for alias in aliases:
            if alias in df.columns:
                rename_map[alias] = standard_name
                break

    if rename_map:
        df = df.rename(columns=rename_map)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "Input file is missing required columns: "
            + ", ".join(missing_columns)
            + f"\nExpected input: {INPUT_PATH}"
        )

    return df


def clean_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def ownership_scale_category(num_properties: int) -> str:
    if num_properties <= 1:
        return "single-property"
    if num_properties <= 10:
        return "small-scale"
    if num_properties <= 50:
        return "mid-scale"
    if num_properties <= 200:
        return "large-scale"
    return "very-large-scale"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Ownership-scale input file not found.\n"
            f"Expected: {INPUT_PATH}\n"
            "The R ownership-share filtering step should write the filtered parcel dataset here."
        )

    PARCEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARCEL_OUTPUT_XLSX_PATH.parent.mkdir(parents=True, exist_ok=True)
    OWNER_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH, low_memory=False)
    df = standardize_columns(df)

    df["owner_name_clean"] = clean_text(df["owner_name"])
    df["owner_address_clean"] = clean_text(df["owner_address"])

    df["owner_entity"] = (
        df["owner_name_clean"] + " | " + df["owner_address_clean"]
    ).str.strip(" |")

    owner_scale = (
        df.groupby("owner_entity", dropna=False)
        .agg(
            owner_name=("owner_name_clean", "first"),
            owner_address=("owner_address_clean", "first"),
            num_properties=("owner_entity", "size"),
        )
        .reset_index()
        .sort_values("num_properties", ascending=False)
    )

    owner_scale["ownership_scale_category"] = owner_scale["num_properties"].apply(
        ownership_scale_category
    )
    owner_scale["ownership_scale_score"] = owner_scale["num_properties"].apply(
        lambda n: math.log10(n + 1)
    )

    df_out = df.merge(
        owner_scale[
            [
                "owner_entity",
                "num_properties",
                "ownership_scale_category",
                "ownership_scale_score",
            ]
        ],
        on="owner_entity",
        how="left",
    )

    df_out["num_other_properties"] = df_out["num_properties"].fillna(0).astype(int) - 1

    df_out = df_out.drop(columns=["owner_name", "owner_address"], errors="ignore")
    df_out = df_out.rename(
        columns={
            "owner_name_clean": "owner_name",
            "owner_address_clean": "owner_address",
        }
    )

    output_columns = [
        "parcel_id",
        "owner_name",
        "owner_address",
        "situs_address",
        "situs_lat",
        "situs_long",
        "owner_entity",
        "num_properties",
        "num_other_properties",
        "ownership_scale_category",
        "ownership_scale_score",
    ]

    output_columns = [column for column in output_columns if column in df_out.columns]
    df_out = df_out[output_columns]

    df_out.to_csv(PARCEL_OUTPUT_PATH, index=False)
    df_out.to_excel(PARCEL_OUTPUT_XLSX_PATH, index=False)
    owner_scale.to_excel(OWNER_OUTPUT_PATH, index=False)

    print(f"Wrote parcel-level output: {PARCEL_OUTPUT_PATH}")
    print(f"Wrote parcel-level Excel output: {PARCEL_OUTPUT_XLSX_PATH}")
    print(f"Wrote owner-level output: {OWNER_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
