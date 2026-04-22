#!/usr/bin/env python
import argparse
import json
from pathlib import Path
import sys
import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Load and validate SynVerse inputs.") # Creates a command line argument parser object.
    parser.add_argument("--config", required=True, help="Path to SynVerse YAML config.") # Adds a required command line argument for the config file path.
    return parser.parse_args() # Parses the command line arguments and returns them as a Namespace object.





def resolve_path(base_dir: Path, value: str) -> str: # Takes a base directory and a relative path value, resolves it to an absolute path, and returns it as a string.
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return str(path.resolve()) # .Resolve(): Resolves any symbolic links and returns the absolute path as a string.



FEATURE_FILE_MAP = {
    "MACCS":    "maccs_file",
    "MFP":      "mfp_file",
    "ECFP_4":   "ecfp_file",
    "mol_graph":"mol_graph_file",
    "smiles":   "smiles_file",
    "target":   "target_file",
    "d1hot":    None,          
}


def main():
    args = parse_args() # Parses the command line arguments.
    repo_root = Path(__file__).resolve().parents[1]
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    config_path = config_path.resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as handle: # Opens the config file for reading .
        config = yaml.safe_load(handle) # Reads YAML and converts it into a Python dictionary.

    repo_root = Path(__file__).resolve().parents[1] # Current_Script_File path is resolved to an absolute path, then go two levels up to get the repository root directory.
    input_settings = config["input_settings"] # Retrieves the "input_settings" section from the config dictionary.
    output_settings = config["output_settings"] # Retrieves the "output_settings" section from the config dictionary.

    input_dir = resolve_path(repo_root, input_settings["input_dir"]) # Resolves the input directory path relative to the repository root and converts it to an absolute path.
    output_dir = resolve_path(repo_root, output_settings["output_dir"]) # Resolves the output directory path relative to the repository root and converts it to an absolute path.

    input_files_raw  = input_settings["input_files"]
    active_features  = [f["name"] for f in config.get("drug_features", [])]

    input_files = {
        "synergy_file": resolve_path(Path(input_dir), input_files_raw["synergy_file"])
    }

    for feature, file_key in FEATURE_FILE_MAP.items():
        if feature in active_features:
            input_files[file_key] = resolve_path(Path(input_dir), input_files_raw[file_key])

    missing = [p for p in input_files.values() if not Path(p).exists()]
    if missing:
        raise FileNotFoundError("Missing input files:\n" + "\n".join(missing))

    manifest = {
        "config":          str(config_path),
        "input_dir":       input_dir,
        "output_dir":      output_dir,
        "score_name":      input_settings["score_name"],
        "active_features": active_features,
        "input_files":     input_files,
    }

    Path("loaded_inputs.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
