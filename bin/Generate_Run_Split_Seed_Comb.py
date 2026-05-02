
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Run_Split_Seed_Combinations.")
    parser.add_argument("--Parsed_config", required=True, help="Path to parsed config file.")
    parser.add_argument("--seed_dict", required=True, help="Path to seed dictionary file.")
    return parser.parse_args()



def load_parsed_config(path):
    with open(Path(path), "rb") as f:
        data = pickle.load(f)
    return data['inputs'], data['params']


def load_seed_dict(path):
    with open(Path(path), "rb") as f:
        seed_dict = pickle.load(f)
    return seed_dict

def main():
    args = parse_args()
    inputs, params = load_parsed_config(args.Parsed_config)
    seed_dict = load_seed_dict(args.seed_dict)
    run_split_seed_combinations = []

    
    for run_no in range(params.start_run, params.end_run):
        for split in params.splits:
            seed = seed_dict[split['type']][run_no]
            run_split_seed_combinations.append((run_no, split['type'], seed))

    with open("run_split_seed_combinations.pkl", "wb") as f:
        pickle.dump(run_split_seed_combinations, f)
     
    