#!/usr/bin/env python3

import argparse
import pickle
import json
from types import SimpleNamespace
from pathlib import Path


from utils import (
    combine_hyperparams,
    create_file_prefix,
    get_select_model_info,
    keep_selected_feat,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare and run one SynVerse training/evaluation job."
    )
    parser.add_argument("--run_no", type=int, required=True)
    parser.add_argument("--split_type", required=True)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--test_file", required=True)
    parser.add_argument("--train_file", required=True)
    parser.add_argument("--train_idx_file", required=True)
    parser.add_argument("--val_idx_file", required=True)
    parser.add_argument("--dfeat_file", required=True)
    parser.add_argument("--cfeat_file", required=True)
    parser.add_argument("--drug_feat", required=True)
    parser.add_argument("--cell_feat", required=True)
    parser.add_argument("--params_json", required=True)
    return parser.parse_args()


def load_pickle(path):
    with open(Path(path), "rb") as handle:
        return pickle.load(handle)


def load_json(path):
    with open(Path(path), "r") as handle:
        return json.load(handle)


def load_params(path):
    return SimpleNamespace(**load_json(path))









def main():
    args = parse_args()

    seed_str = str(args.seed).lower()
    if seed_str in ("null", "none", ""):
        seed = None
    else:
        seed = int(args.seed)

    params = load_params(args.params_json)

    test_df = load_pickle(args.test_file)
    all_train_df = load_pickle(args.train_file)
    train_idx = load_pickle(args.train_idx_file)
    val_idx = load_pickle(args.val_idx_file)
    cur_dfeat_dict = load_pickle(args.dfeat_file)
    cur_cfeat_dict = load_pickle(args.cfeat_file)
    select_drug_feat = args.drug_feat
    select_cell_feat = args.cell_feat
    
    print("drug and cell line features in use:", select_drug_feat, select_cell_feat)

    select_dfeat_dict = keep_selected_feat(cur_dfeat_dict, select_drug_feat)
    select_cfeat_dict = keep_selected_feat(cur_cfeat_dict, select_cell_feat)

    select_model_info = get_select_model_info(params.model_info, select_dfeat_dict['encoder'], select_cfeat_dict['encoder'])
    params.hyperparam = combine_hyperparams(select_model_info)
    given_epochs = params.epochs



    # select_model_info = get_select_model_info(
    #     params.model_info,
    #     select_dfeat_dict["encoder"],
    #     select_cfeat_dict["encoder"],
    # )

    # params.hyperparam = combine_hyperparams(select_model_info)
    # given_epochs = params.epochs
    # feat_str = f"D_{'_'.join(select_drug_feat)}_C_{'_'.join(select_cell_feat)}"

    # out_file_prefix = create_file_prefix(
    #     params,
    #     select_dfeat_dict,
    #     select_cfeat_dict,
    #     args.split_type,
    #     split_feat_str=feat_str,
    #     run_no=args.run_no,
    #     seed=seed,
    # )

    


if __name__ == "__main__":
    main()
