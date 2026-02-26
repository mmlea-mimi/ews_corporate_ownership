# src/00_ingest_targets.R
# Purpose:
#  - Read data/raw/target_properties.xlsx
#  - Extract a clean list of parcel IDs (pID)
#  - Write data/interim/targets_parcel_ids.csv
#  - Write a quick summary to outputs/targets_summary.txt

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(janitor)
  library(readr)
})

in_path <- "data/raw/target_properties.xlsx"
out_csv <- "data/interim/targets_parcel_ids.csv"
out_summary <- "outputs/targets_summary.txt"

dir.create("data/interim", recursive = TRUE, showWarnings = FALSE)
dir.create("outputs", recursive = TRUE, showWarnings = FALSE)

# Read first sheet by default (change if needed)
df_raw <- readxl::read_excel(in_path, col_names = FALSE)

# Make temporary column names like v1, v2, v3...
names(df_raw) <- paste0("v", seq_len(ncol(df_raw)))

df <- df_raw

# Heuristic: pID is usually a 6–8 digit-ish identifier (often numeric in Excel)
# We'll look for the column with the most values that look like an integer ID.
score_pid_col <- function(x) {
  x <- as.character(x)
  x <- x[!is.na(x)]
  x <- trimws(x)
  if (length(x) == 0) return(0)
  mean(grepl("^[0-9]{5,10}$", x))
}

col_scores <- sapply(df, score_pid_col)
pid_col <- names(which.max(col_scores))

if (max(col_scores) < 0.3) {
  stop(
    "I couldn't confidently detect a pID column. Column scores were:\n",
    paste(names(col_scores), round(col_scores, 3), sep="=", collapse=", "),
    "\nOpen the Excel and tell me which column contains parcel IDs, then set pid_col <- 'v#'."
  )
}

targets <- df |>
  transmute(pID = as.character(.data[[pid_col]])) |>
  filter(!is.na(pID), pID != "") |>
  distinct()

readr::write_csv(targets, out_csv)

summary_lines <- c(
  paste("Input file:", in_path),
  paste("Detected parcel id column:", pid_col),
  paste("Rows in input:", nrow(df)),
  paste("Distinct pIDs written:", nrow(targets)),
  paste("Duplicates removed:", nrow(df) - nrow(distinct(df, .data[[pid_col]])))
)

writeLines(summary_lines, out_summary)

message("Wrote: ", out_csv)
message("Wrote: ", out_summary)
