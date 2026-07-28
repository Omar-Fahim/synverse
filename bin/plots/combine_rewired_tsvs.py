#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd


DEFAULT_SPLITS = [
    "random",
    "leave_comb",
    "leave_drug",
    "leave_cell_line",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Combine SA and SM output_<split>_rewired.tsv files into one correctly "
            "named file per split."
        )
    )
    parser.add_argument("--sa-dir", required=True, type=Path, help="Folder containing SA rewired TSV files.")
    parser.add_argument("--sm-dir", required=True, type=Path, help="Folder containing SM rewired TSV files.")
    parser.add_argument("--out-dir", required=True, type=Path, help="Folder where combined TSV files will be written.")
    parser.add_argument(
        "--splits",
        nargs="+",
        default=DEFAULT_SPLITS,
        help="Split names to combine. Default: random leave_comb leave_drug leave_cell_line",
    )
    return parser.parse_args()

# This function reads a rewired TSV file and checks that it contains the required columns.
def read_rewired_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path, sep="\t")
    required_columns = {"rewired", "rewire_method"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"{path} is missing required columns: {sorted(missing_columns)}")

    return df

# This method is used to combine the rewired tsv files from the SA and SM runs into one file for each split. 
# The combined file will have the same columns as the original files, but will contain all rows from both files. 
# The combined file will be written to the out_dir with the same name as the original files.
def combine_split(sa_dir, sm_dir, out_dir, split):
    file_name = f"output_{split}_rewired.tsv"
    sa_file = sa_dir / file_name
    sm_file = sm_dir / file_name
    out_file = out_dir / file_name

    source_files = [sa_file.resolve(), sm_file.resolve()]

    sa_df = read_rewired_file(sa_file)
    sm_df = read_rewired_file(sm_file)

    if list(sa_df.columns) != list(sm_df.columns):
        raise ValueError(
            f"Column mismatch for {file_name}. SA columns and SM columns must match after "
            "setting rewired/rewire_method."
        )
    
    # Combine the two dataframes into one, keeping all rows from both dataframes.
    combined_df = pd.concat([sa_df, sm_df], axis=0, ignore_index=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_file = out_file.with_suffix(out_file.suffix + ".tmp")
    combined_df.to_csv(tmp_file, sep="\t", index=False)
    tmp_file.replace(out_file)

    print(f"Wrote {out_file}")
    print(f"Kept {sa_file}")
    print(f"Kept {sm_file}")


def main():
    args = parse_args()

    for split in args.splits:
        combine_split(
            sa_dir=args.sa_dir,
            sm_dir=args.sm_dir,
            out_dir=args.out_dir,
            split=split,
        )


if __name__ == "__main__":
    main()
