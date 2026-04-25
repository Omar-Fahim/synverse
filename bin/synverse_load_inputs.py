#!/usr/bin/env python
import argparse
import json
import os
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
      
}

CELL_LINE_FEATURE_FILE_MAP = {
    "genex": ["genex_file"],
    "genex_lincs_1000": ["genex_file", "lincs"],
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

    input_files  = input_settings["input_files"]
    active_drug_feature_names  = [f["name"] for f in config.get("drug_features", [])] # Read drug features from config and create a list of active feature names.

    config_errors = []

    # validate synergy_file exists in config and is a non-empty path-like string
    synergy_file= input_files.get("synergy_file")
    if synergy_file is None:
        config_errors.append("'synergy_file' is missing from input_files in the config")
    elif not isinstance(synergy_file, (str, os.PathLike)):
        raise TypeError("Value for 'synergy_file' must be a path string")
    elif str(synergy_file).strip() == "":
        config_errors.append("Value for 'synergy_file' is empty")

   
    if config_errors:
        raise ValueError("\n".join(config_errors))

    input_files_paths = {} 
    input_files_paths["synergy_file"] = resolve_path(Path(input_dir), str(synergy_file))

# Validate that all active features have corresponding file keys in the config and that those file paths are valid.
    for feature, file_key in FEATURE_FILE_MAP.items():
  
        if feature in active_drug_feature_names:
            if input_files.get(file_key) is None:
                config_errors.append(f"Feature '{feature}' is active but has no corresponding file key in the config")
                continue

            if not isinstance(input_files.get(file_key), (str, os.PathLike)):
                raise TypeError(f"Value for '{file_key}' must be a path string")

            if str(input_files.get(file_key)).strip() == "":
                config_errors.append(f"Value for '{file_key}' is empty")
                continue

           
            resolved_path = resolve_path(Path(input_dir), str(input_files.get(file_key)))
            if not Path(resolved_path).exists():
                config_errors.append(f"File for '{file_key}' does not exist: {resolved_path}")
            else:
                input_files_paths[file_key] = resolved_path

    
    

    if config_errors:
        raise ValueError("\n".join(config_errors))

    
    active_cell_line_feature_names  = [f["name"] for f in config.get("cell_line_features", [])]

    for feature, file_keys in CELL_LINE_FEATURE_FILE_MAP.items():
        if feature in active_cell_line_feature_names:
            for file_key in file_keys:
                if input_files.get(file_key) is None:
                    config_errors.append(f"Feature '{feature}' is active but has no corresponding file key '{file_key}' in the config")
                    continue

                if str(input_files.get(file_key)).strip() == "":
                    config_errors.append(f"Value for '{file_key}' is empty")
                    continue
                    
                if not isinstance(input_files.get(file_key), (str, os.PathLike)):
                    raise TypeError(f"Value for '{file_key}' must be a path string")

                

               resolved_path = resolve_path(Path(input_dir), str(input_files.get(file_key)))
               if not Path(resolved_path).exists():
                    config_errors.append(f"File for '{file_key}' does not exist: {resolved_path}")
               else:
                    input_files_paths[file_key] = resolved_path

    if config_errors:
        raise ValueError("\n".join(config_errors))
        
    manifest = {
        "config":          str(config_path),
        "input_dir":       input_dir,
        "output_dir":      output_dir,
        "score_name":      input_settings["score_name"],
        "active_features": {
            "drug": active_drug_feature_names,
            "cell_line": active_cell_line_feature_names,
        },
        "input_files":     input_files,
        "input_files_abs_paths": input_files_paths,
    }

    Path("loaded_inputs.json").write_text( # Writes the manifest dictionary as a JSON string to a file named "loaded_inputs.json" in the current working directory.
        json.dumps(manifest, indent=2), 
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
