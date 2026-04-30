#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from parse_config import parse_config
import pickle 
import os

#Drug Preprocess imports
from rdkit import Chem
from preprocessing.rwr_runner import *
from models.model_utils import *
from preprocessing.pretrain.embedding_generator import get_pretrained_embedding
import torch
from torch_geometric import data as DATA
from preprocess_utils import adjacency_list_to_edges


#Cell line preprocess imports
import pandas as pd
import numpy as np

#Load_Triplets Preprocess
from preprocessing.synergy_data_preprocess import *
from preprocessing.autoencoder import autoencoder_runner
from preprocessing.preprocess_utils import *
from preprocessing.preprocess import load_filter_triplets_features
from utils import *
from split import *
#Panda already above


def parse_args():
    parser = argparse.ArgumentParser(description="Load and validate SynVerse inputs.") # Creates a command line argument parser object.
    parser.add_argument("--manifest", required=True, help="Path to SynVerse YAML Manifest.") # Adds a required command line argument for the config file path.
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










def load_dataframes(params, inputs, device):
    synergy_file_path = inputs.synergy_file
    score_name = params.score_name
    synergy_df = load_synergy_file(synergy_file_path, score_name)

    drug_pids = sorted(list(set(synergy_df['drug_1_pid']).union(set(synergy_df['drug_2_pid']))))
    cell_line_names = sorted(synergy_df['cell_line_name'].unique())

    # dfeat_dict, dfeat_names = prepare_drug_features(drug_pids, params, inputs, device)
    # cfeat_dict, cfeat_names = prepare_cell_line_features(cell_line_names, params, inputs, device)

    synergy_df, dfeat_dict, cfeat_dict, drug_2_idx, cell_line_2_idx = load_filter_triplets_features(synergy_df, drug_pids, cell_line_names, inputs, params, device)
    drug_cell_feat_combs = get_feature_comb_wrapper(dfeat_dict, cfeat_dict,
                            max_drug_feat=params.max_drug_feat,
                            min_drug_feat = params.min_drug_feat, max_cell_feat=params.max_cell_feat, min_cell_feat = params.min_cell_feat)
    return synergy_df, dfeat_dict, cfeat_dict, drug_cell_feat_combs


def main():
    args = parse_args()
    manifest = load_manifest(args.manifest)
    config_map = manifest.get("config_map")

    if config_map is None:
        raise ValueError("Parsed config not found in manifest.")

    inputs, params = parse_config(config_map)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    synergy_df, dfeat_dict, cfeat_dict, drug_cell_feat_combs = load_dataframes(params, inputs, device)
    synergy_df.to_csv("synergy_df.tsv", sep="\t", index=False)



    with open("drug_features.pkl", "wb") as f:
        pickle.dump(dfeat_dict, f)

    with open("cell_features.pkl", "wb") as f:
        pickle.dump(cfeat_dict, f)
                               
    with open("drug_cell_feat_combs.pkl", "wb") as f:
        pickle.dump(drug_cell_feat_combs, f)


        
if __name__ == "__main__":
    main()