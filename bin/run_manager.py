import os.path

from models.runner import *
from utils import *

class BaseRunManager:
    def __init__(self, params, model_info, given_epochs, train_df, train_idx, val_idx,
                 dfeat_dict, cfeat_dict, test_df, drug_2_idx,cell_line_2_idx,out_file_prefix,file_prefix, device):
        self.params = params
        self.model_info = model_info
        self.given_epochs = given_epochs
        self.train_df = train_df
        self.train_idx = train_idx
        self.val_idx = val_idx
        self.dfeat_dict = dfeat_dict
        self.cfeat_dict = cfeat_dict
        self.test_df = test_df
        self.drug_2_idx = drug_2_idx
        self.cell_line_2_idx = cell_line_2_idx
        self.file_prefix = file_prefix
        self.out_file_prefix = out_file_prefix
        self.device = device
        

    def execute_run(self, train_df, train_idx, val_idx, dfeat_dict, cfeat_dict, out_file_prefix):

        #pipeline for training a model
        hyperparam = self.params.hyperparam
        runner = Runner(train_df, train_idx, val_idx, dfeat_dict, cfeat_dict,
                        out_file_prefix, self.params, self.model_info,
                        self.device)

        # if self.params.hp_tune:
        #     runner.find_best_hyperparam(self.params.bohb['server_type'])

        hyperparam_file = self.out_file_prefix + '_best_hyperparam.txt'
        if os.path.exists(hyperparam_file):
            hyperparam, _ = extract_best_hyperparam(hyperparam_file)
            print('Found hyperparam file: ', out_file_prefix)
        else:
            if self.params.use_best_hyperparam:
                sys.exit(f"Error: hyperparameter file not found ({hyperparam_file}) but use_best_hyperparam=True")
            else:
                print(f'File: {hyperparam_file} not found for best hyperparam. Running with default hyperparameters.')

        trained_model_state, train_loss = runner.train_model_given_config(hyperparam, self.given_epochs, validation=True, save_output=True)

        #testing a model
        runner.get_test_score(self.test_df, trained_model_state, hyperparam, save_output=True, file_prefix=self.file_prefix)

    def run_wrapper(self):
        self.execute_run(self.train_df, self.train_idx, self.val_idx, self.dfeat_dict, self.cfeat_dict, self.out_file_prefix)

class RunManagerFactory:
    @staticmethod
    def get_run_manager(params, model_info, given_epochs, train_df, train_idx, val_idx,
                        dfeat_dict, cfeat_dict, test_df, drug_2_idx, cell_line_2_idx,
                        out_file_prefix, file_prefix, device,train_type):

        
        cls = {
            "regular": BaseRunManager
        }.get(train_type, BaseRunManager)

        return cls(params, model_info, given_epochs, train_df, train_idx, val_idx,
                   dfeat_dict, cfeat_dict, test_df, drug_2_idx, cell_line_2_idx,
                   out_file_prefix, file_prefix, device)





