#!/usr/bin/env python3
import pandas as pd
import argparse, os, pickle
import copy
from utils import wrapper_test_train_val, remove_self_loop_from_splits,split_type_map
import json
from pathlib import Path
from preprocessing.preprocess import post_split_processing
from utils import get_feat_prefix
import torch
from graph_split import split_cv
def parse_args():
    parser = argparse.ArgumentParser(description="Split dataset into train, validation, and test sets.")
    parser.add_argument("--run_no", type=int, required=True, help="Run number for reproducibility.")
    parser.add_argument("--split_type", type=str, required=True, help="Split type.")
    parser.add_argument("--test_frac", type=float, required=True, help="Test fraction.")
    parser.add_argument("--val_frac", type=float, required=True, help="Validation fraction.")
    parser.add_argument("--seed", type=str, required=True, help="Random seed for reproducibility (int or 'null').")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to the input dataset file (CSV).")
    parser.add_argument("--parsed_config_path", type=str, required=True, help="Path to the parsed config file (pickle).")
    parser.add_argument("--dfeat_dict", type=str, required=True, help="Path to the parsed drug features file (pickle).")
    parser.add_argument("--cfeat_dict", type=str, required=True, help="Path to the parsed cell line features file (pickle).")

    return parser.parse_args()

def load_dict_from_pickle(path):
    with open(Path(path), "rb") as f:
        data = pickle.load(f)
    return data
    
def load_parsed_config(path):
    with open(Path(path), "rb") as f:
        data = pickle.load(f)
    return data['inputs'], data['params']

def main():

    args = parse_args()

    # Normalize seed: Nextflow may pass the literal string 'null' when no seed
    # is configured. Accept 'null' (case-insensitive) and empty strings as None.
    seed_arg = args.seed
   
    seed_str = str(seed_arg).lower()
    if seed_str in ("null", "none", ""):
        seed = None
    else:
        seed = int(seed_arg)
            
    print(f" parsed_config_path: {args.parsed_config_path}")


    

    inputs, params = load_parsed_config(args.parsed_config_path)

    # Load the synergy dataset and split settings for this run.
    synergy_df = pd.read_csv(args.dataset_path, sep="\t")
    split_type = args.split_type
    test_frac = args.test_frac
    val_frac = args.val_frac


    
    
    #test_df, all_train_df, train_idx, val_idx = wrapper_test_train_val(copy.deepcopy(synergy_df), split_type, test_frac, val_frac, seed = seed)
    cv_settings = getattr(params, 'cv', {'enabled': False, 'n_folds': 5})
    cv_enabled = cv_settings.get('enabled', False)

    if params.train_type == 'regular' and cv_enabled:
        #When CV is enabled for regular training, treat args.run_no as the fold index.
        #Each fold gets its own test set, and the remaining folds are used for training without an additional validation split.
        n_folds = int(cv_settings.get('n_folds', 5))
        fold_no = int(args.run_no)
        # Here cross-validation split is performed
        train_folds, test_folds = split_cv(
            copy.deepcopy(synergy_df),
            split_type_map[split_type],
            n_folds=n_folds,
            seed=seed
        )
        
        test_df = synergy_df.iloc[test_folds[fold_no]].copy()
        all_train_df = synergy_df.iloc[train_folds[fold_no]].reset_index(drop=True)

        train_idx = {0: list(range(len(all_train_df)))}
        val_idx = {0: []}

    else:
    # create one train/validation/test split using the split strategy and fractions in the config
        test_df, all_train_df, train_idx, val_idx = wrapper_test_train_val(
            copy.deepcopy(synergy_df),
            split_type,
            test_frac,
            val_frac,
            seed=seed
        )
    





    # Remove self-loops from the splits
    test_df, all_train_df, train_idx, val_idx = remove_self_loop_from_splits( test_df, all_train_df, train_idx, val_idx)
    # Select only the relevant columns for the output
    all_train_df = all_train_df[['source', 'target','edge_type', params.score_name]]

    # load feature dictionaries from the pickled files passed as arguments
    with open(args.dfeat_dict, 'rb') as fh:
        dfeat_dict = pickle.load(fh)
    with open(args.cfeat_dict, 'rb') as fh:
        cfeat_dict = pickle.load(fh)

    # expose run_no, seed and device variables used later
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    feat_str = get_feat_prefix(dfeat_dict, cfeat_dict)
    seed_str = "null" if seed is None else str(seed)
    split_info_str = f"/{feat_str}/k_{params.abundance}_{params.score_name}/{split_type}_{test_frac}_{val_frac}/run_{args.run_no}_{seed_str}/"
    split_file_path = params.split_dir + split_info_str
    cur_dfeat_dict, cur_cfeat_dict = post_split_processing(dfeat_dict, cfeat_dict, all_train_df, params, split_info_str, device)


    # save the splits in files (run,split_type,seed)

    # out_dir = os.path.join("results", f"run_{args.run_no}", f"split_{split_type}", f"seed_{args.seed}")
    # os.makedirs(out_dir, exist_ok=True)
    # test_path = os.path.join(out_dir, "test.pkl")
    # train_path = os.path.join(out_dir, "train.pkl")
    # train_idx_path = os.path.join(out_dir, "train_idx.pkl")
    # val_idx_path = os.path.join(out_dir, "val_idx.pkl")
    # print(f"Saving test set to: {test_path}")
    
    # Print for testing
    # print(f"Test set size: {len(test_df)}")
    # print(f"Train set size: {len(all_train_df)}")
    # print(f"Train indices : {train_idx.get(0)}")
    # print(f"Validation indices : {val_idx.get(0)}")
    

    with open('test.pkl', "wb") as f:
        pickle.dump(test_df, f)

    with open('train.pkl', "wb") as f:
        pickle.dump(all_train_df, f)

    with open('train_idx.pkl', "wb") as f:
        pickle.dump(train_idx, f)

    with open('val_idx.pkl', "wb") as f:
        pickle.dump(val_idx, f)
    with open('cur_dfeat_dict.pkl', "wb") as f:
        pickle.dump(cur_dfeat_dict, f)
    with open('cur_cfeat_dict.pkl', "wb") as f:
        pickle.dump(cur_cfeat_dict, f)


if __name__ == "__main__":
    main()
    







