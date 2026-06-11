#!/usr/bin/env python
import argparse
import json
import os, pickle
from pathlib import Path
from parse_config import parse_config
import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Load and validate SynVerse inputs.") # Creates a command line argument parser object.
    parser.add_argument("--config", required=True, help="Path to SynVerse YAML config.") # Adds a required command line argument for the config file path.
    return parser.parse_args() # Parses the command line arguments and returns them as a Namespace object.





def resolve_path(base_dir: Path, value: str) -> Path: # Takes a base directory and a relative path value, resolves it to an absolute path, and returns it as a Path.
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve() # .Resolve(): Resolves any symbolic links and returns the absolute path.



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
    print(f"Parsed arguments: {args}") # Prints the parsed arguments for debugging purposes.
    # repo_root = Path(__file__).resolve().parents[1]
    # config_path = Path(args.config)
    # if not config_path.is_absolute():
    #     config_path = repo_root / config_path
    # config_path = config_path.resolve()
    # print(f"Resolved config path: {config_path}")
    config_path = Path(args.config).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as handle: # Opens the config file for reading .
        config = yaml.safe_load(handle) # Reads YAML and converts it into a Python dictionary.

    repo_root = Path(__file__).resolve().parents[1] # Current_Script_File path is resolved to an absolute path, then go two levels up to get the repository root directory.
    input_settings = config["input_settings"] # Retrieves the "input_settings" section from the config dictionary.
    output_settings = config["output_settings"] # Retrieves the "output_settings" section from the config dictionary.
    input_dir_str = os.path.expandvars(input_settings["input_dir"])
    input_dir = resolve_path(repo_root, input_dir_str)
    #input_dir = resolve_path(repo_root, input_settings["input_dir"]) # Resolves the input directory path relative to the repository root and converts it to an absolute Path.
    output_dir = resolve_path(repo_root, output_settings["output_dir"]) # Resolves the output directory path relative to the repository root and converts it to an absolute Path.

    input_files  = input_settings["input_files"]
    active_drug_feature_names  = [f["name"] for f in input_settings.get("drug_features", [])] # Read drug features from config and create a list of active feature names.

    config_errors = []

    # Here I check that the  synergy_file exists in config and is a non-empty pathstring
    synergy_file= input_files.get("synergy_file")
    if synergy_file is None:
        config_errors.append("'synergy_file' is missing from input_files in the config")
    elif not isinstance(synergy_file, (str, os.PathLike)):
        raise TypeError("Value for 'synergy_file' must be a path string")
    elif str(synergy_file).strip() == "":
        config_errors.append("Value for 'synergy_file' is empty")

    input_files_paths = {}

  
    if not config_errors:
        resolved_synergy_path = resolve_path(input_dir, str(synergy_file))
        if not resolved_synergy_path.exists():
            config_errors.append(f"File for 'synergy_file' does not exist: {resolved_synergy_path}")
        else:
            input_files_paths["synergy_file"] = str(resolved_synergy_path)

    if config_errors:
        raise ValueError("\n".join(config_errors))


# Here I validate that all active features have corresponding file keys in the config and that those file paths are valid.
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

           
            resolved_path = resolve_path(input_dir, str(input_files.get(file_key)))
            if not resolved_path.exists():
                config_errors.append(f"File for '{file_key}' does not exist: {resolved_path}")
            else:
                input_files_paths[file_key] = str(resolved_path)

    
    

    if config_errors:
        raise ValueError("\n".join(config_errors))

    
    active_cell_line_feature_names  = [f["name"] for f in input_settings.get("cell_line_features", [])]

    for feature, file_keys in CELL_LINE_FEATURE_FILE_MAP.items():
        if feature in active_cell_line_feature_names:
            for file_key in file_keys:
                if input_files.get(file_key) is None:
                    config_errors.append(f"Feature '{feature}' is active but has no corresponding file key '{file_key}' in the config")
                    continue

                if not isinstance(input_files.get(file_key), (str, os.PathLike)):
                    raise TypeError(f"Value for '{file_key}' must be a path string")


                if str(input_files.get(file_key)).strip() == "":
                    config_errors.append(f"Value for '{file_key}' is empty")
                    continue
                    
                

                

                resolved_path = resolve_path(input_dir, str(input_files.get(file_key)))
                if not resolved_path.exists():
                    config_errors.append(f"File for '{file_key}' does not exist: {resolved_path}")
                else:
                    input_files_paths[file_key] = str(resolved_path)

    if config_errors:
        raise ValueError("\n".join(config_errors))
    inputs, params = parse_config(config)
    data = {
        "inputs": inputs,
        "params": params
    }

    with open("loaded_inputs.pkl", "wb") as f:
        pickle.dump(data, f)

    with open("inputs.json", "w") as f:
        json.dump(vars(inputs), f, indent=2)

    with open("params.json", "w") as f:
        json.dump(vars(params), f, indent=2)

if __name__ == "__main__":
    main()
