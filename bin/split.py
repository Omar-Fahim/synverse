import pandas as pd
import os
import copy
import pickle

split_type_map = {'random': 'random', 'leave_comb': 'edge', 'leave_drug':'node', 'leave_cell_line': 'edge_type'}



# def wrapper_train_test(df, split_type, test_frac, spec_dir, seed=None):
#     '''Rename column names to more generalized ones. Also, convert drug and cell line ids to numerical ids compatible with models.'''
#     test_file = f'{spec_dir}/test.tsv'
#     train_file = f'{spec_dir}/train.tsv'
#     all_triplets_file = f'{spec_dir}/all.tsv'
#     summary = f'{spec_dir}/train_test_summary.txt'
#
#
#     print('Creating train test folds')
#     train_idx, test_idx = split_train_test(df, split_type_map[split_type], test_frac, seed)
#
#     train_df = df.iloc[train_idx]
#     test_df = df.iloc[test_idx]
#
#     os.makedirs(spec_dir, exist_ok=True)
#     test_df.to_csv(test_file, sep='\t')
#     train_df.to_csv(train_file, sep='\t')
#     df.to_csv(all_triplets_file, sep='\t')
#
#     test_drugs = set(test_df['source']).union(set(test_df['target']))
#     test_cell_lines = set(test_df['edge_type'])
#     print(f'TEST #triplets: {len(test_df)} \n #drugs: {len(test_drugs)}'
#           f' \n #cell lines: {len(test_cell_lines)}')
#
#     with open(summary, 'w') as file:
#         file.write(f'TEST #triplets: {len(test_df)} \n #drugs: {len(test_drugs)}'
#           f' \n #cell lines: {len(test_cell_lines)}')
#     file.close()
#     # return train_df, test_df, drug_2_idx, cell_line_2_idx
#     return train_df, test_df

def wrapper_test_train_val(df, split_type, test_frac, val_frac, spec_dir, seed=None, force_run=False):
    print(split_type)
    test_file = f'{spec_dir}/test.tsv'
    all_train_file = f'{spec_dir}/all_train.tsv'
    train_file =  f'{spec_dir}/train.pkl'
    val_file =  f'{spec_dir}/val.pkl'
    all_triplets_file = f'{spec_dir}/all.tsv'

    summary = f'{spec_dir}/train_test_val_summary.txt'

    os.makedirs(spec_dir, exist_ok=True)
    # print('Creating train test val folds')

    if (not (os.path.exists(test_file) and os.path.exists(train_file) and os.path.exists(val_file))) or force_run:
        print('Creating train test val folds')
        #splitting into train and test
        all_train_idx, test_idx = split_train_test(df, split_type_map[split_type], test_frac, seed)
        all_train_df = df.iloc[all_train_idx].reset_index(drop=True)
        test_df = df.iloc[test_idx]

        #now split the train into val and train to be used in hyperparam tuning
        train_idx, val_idx = split_train_test(all_train_df, split_type_map[split_type], val_frac, seed)
        with open(train_file, 'wb') as file:
            pickle.dump(train_idx, file)
        with open(val_file, 'wb') as file:
            pickle.dump(val_idx, file)


        #save in file
        os.makedirs(spec_dir, exist_ok=True)
        test_df.to_csv(test_file, sep='\t')
        all_train_df.to_csv(all_train_file, sep='\t')
        df.to_csv(all_triplets_file, sep='\t')
    else:
        print(f'Loading train test val data from {spec_dir}')
        test_df = pd.read_csv(test_file, sep='\t', dtype={'drug_1_pid': str, 'drug_2_pid': str})
        all_train_df = pd.read_csv(all_train_file, sep='\t', dtype={'drug_1_pid': str, 'drug_2_pid': str})

        with open(val_file, 'rb') as file:
            val_idx = pickle.load(file)
        with open(train_file, 'rb') as file:
            train_idx = pickle.load(file)

    test_drugs = set(test_df['source']).union(set(test_df['target']))
    test_cell_lines = set(test_df['edge_type'])

    train_df = all_train_df.iloc[train_idx]
    train_drugs = set(train_df['source']).union(set(train_df['target']))
    train_cell_lines = set(train_df['edge_type'])

    val_df = all_train_df.iloc[val_idx]
    val_drugs = set(val_df['source']).union(set(val_df['target']))
    val_cell_lines = set(val_df['edge_type'])
    print(f'TEST #triplets: {len(test_df)} \n #drugs: {len(test_drugs)}'
          f' \n #cell lines: {len(test_cell_lines)}')
    print(f'TRAIN #triplets: {len(train_df)} \n #drugs: {len(train_drugs)}'
          f' \n #cell lines: {len(train_cell_lines)}')
    print(f'VAL #triplets: {len(val_df)} \n #drugs: {len(val_drugs)}'
          f' \n #cell lines: {len(val_cell_lines)}')

    with open(summary, 'w') as file:
        file.write(f'TEST #triplets: {len(test_df)} \n #drugs: {len(test_drugs)}'
                   f' \n #cell lines: {len(test_cell_lines)}\n\n'
                   f'TRAIN #triplets: {len(train_df)} \n #drugs: {len(train_drugs)}'
                   f' \n #cell lines: {len(train_cell_lines)}\n\n'
                   f' VAL #triplets: {len(val_df)} \n #drugs: {len(val_drugs)}'
                   f' \n #cell lines: {len(val_cell_lines)}')
    file.close()

    return test_df, all_train_df, {0:train_idx}, {0:val_idx}

