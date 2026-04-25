
import argparse
import json
from pathlib import Path
import pandas as pd



def parse_args():
    parser = argparse.ArgumentParser(description="Load and validate SynVerse inputs.") # Creates a command line argument parser object.
    parser.add_argument("--manifest", required=True, help="Path to SynVerse YAML config.") # Adds a required command line argument for the config file path.
    return parser.parse_args() # Parses the command line arguments and returns them as a Namespace object.



def load_manifest(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)

def load_synergy_file(path,score_name):
    synergy_df = pd.read_csv(
        path,
        sep="\t",
        dtype={
            "drug_1_pid": str,
            "drug_2_pid": str,
            "cell_line_name": str,
            score_name: float,
        },
    )
    return synergy_df


def main():
    args = parse_args()
    manifest = load_manifest(args.manifest)

    # Extract values from manifest
    input_files = manifest["input_files_abs_paths"]
    score_name = manifest["score_name"]

    # Load synergy file
    df = load_synergy_file(input_files["synergy_file"], score_name)

    print("synergy shape:", df.shape)
                               

if __name__ == "__main__":
    main()