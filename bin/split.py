#!/usr/bin/env python3
import pandas as pd
import argparse, os, pickle
import copy
from utils import wrapper_test_train_val, remove_self_loop_from_splits
import json
from pathlib import Path

#Read run_no,split_type,Seed from command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Split dataset into train, validation, and test sets.")
    parser.add_argument("--run_no", type=int, required=True, help="Run number for reproducibility.")
    parser.add_argument("--split", type=str, required=True, help="Split to perform.")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for reproducibility.")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to the input dataset file (CSV).")
    parser.add_argument("--parsed_config_path", type=str, required=True, help="Path to the parsed config file (pickle).")
    return parser.parse_args()


def load_parsed_config(path):
    with open(Path(path), "rb") as f:
        data = pickle.load(f)
    return data['inputs'], data['params']

def main():
    args = parse_args()

    inputs, params = load_parsed_config(args.parsed_config_path)

    # Load the dataset
    synergy_df = pd.read_csv(args.dataset_path, sep="\t")
    split = json.loads(args.split)

    split_type, test_frac, val_frac =split['type'], split['test_frac'], split['val_frac']



    # Perform the split using the wrapper function
    test_df, all_train_df, train_idx, val_idx = wrapper_test_train_val(copy.deepcopy(synergy_df), split_type, test_frac, val_frac, seed = args.seed)
    # Remove self-loops from the splits
    test_df, all_train_df, train_idx, val_idx = remove_self_loop_from_splits( test_df, all_train_df, train_idx, val_idx)
    # Select only the relevant columns for the output
    all_train_df = all_train_df[['source', 'target','edge_type', params.score_name]]

    # save the splits in files (run,split_type,seed)

    out_dir = os.path.join("results", f"run_{args.run_no}", f"split_{split_type}", f"seed_{args.seed}")
    os.makedirs(out_dir, exist_ok=True)
    test_path = os.path.join(out_dir, "test.pkl")
    train_path = os.path.join(out_dir, "train.pkl")
    train_idx_path = os.path.join(out_dir, "train_idx.pkl")
    val_idx_path = os.path.join(out_dir, "val_idx.pkl")
    print(f"Saving test set to: {test_path}")
    
    # Print for testing
    print(f"Test set size: {len(test_df)}")
    print(f"Train set size: {len(all_train_df)}")
    print(f"Train indices : {train_idx.get(0)}")
    print(f"Validation indices : {val_idx.get(0)}")
    

    with open(test_path, "wb") as f:
        pickle.dump(test_df, f)

    with open(train_path, "wb") as f:
        pickle.dump(all_train_df, f)

    with open(train_idx_path, "wb") as f:
        pickle.dump(train_idx, f)

    with open(val_idx_path, "wb") as f:
        pickle.dump(val_idx, f)


if __name__ == "__main__":
    main()
    







