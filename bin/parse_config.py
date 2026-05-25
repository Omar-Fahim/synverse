from dataclasses import dataclass
from typing import Any, Optional
import os


@dataclass
class Inputs:
    synergy_file: str
    maccs_file: Optional[str] = None
    mfp_file: Optional[str] = None
    ecfp_file: Optional[str] = None
    smiles_file: Optional[str] = None
    mol_graph_file: Optional[str] = None
    target_file: Optional[str] = None
    genex_file: Optional[str] = None
    lincs: Optional[str] = None
    vocab_file: Optional[str] = None
    net_file: Optional[str] = None
    prot_info_file: Optional[str] = None


@dataclass
class Params:
    score_name: str
    drug_features: Any
    cell_line_features: Any
    model_info: Any
    epochs: int
    autoencoder_dims: Any
    splits: Any
    abundance: float
    max_drug_feat: int
    max_cell_feat: int
    min_drug_feat: int
    min_cell_feat: int
    hp_tune: bool
    rewire_method: str
    batch_size: int
    wandb: Any
    bohb: Any
    input_dir: str
    out_dir: str
    split_dir: str
    start_run: int
    end_run: int
    seeds:  dict[str, list[int]]
    train_type: str  
    use_best_hyperparam: bool = False  
    split_type: str = ''  # Added split_type to Params


def parse_config(config_map):
    input_settings = config_map['input_settings']
    input_dir = input_settings['input_dir']
    out_dir = config_map['output_settings']['output_dir']

    # Make paths absolute
    code_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(code_dir, os.pardir))

    if not os.path.isabs(input_dir):
        input_dir = os.path.join(project_root, input_dir)
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(project_root, out_dir)

    # Create Inputs dataclass
    inputs = Inputs(
        **{key: f"{input_dir}/{value}" for key, value in input_settings['input_files'].items()}
    )

    # Create Params dataclass
    params = Params(
        score_name=input_settings['score_name'],
        drug_features=input_settings['drug_features'],
        cell_line_features=input_settings['cell_line_features'],
        model_info=input_settings['model_info'],

        epochs=input_settings.get('epochs', 1500),
        batch_size=input_settings.get('batch_size', 4096),
        autoencoder_dims=input_settings.get(
            'autoencoder_dims',
            [[1024, 512], [512, 256], [256, 128], [256, 64]]
        ),
        splits=input_settings['splits'],

        abundance=input_settings.get('abundance', 0.05),
        max_drug_feat=input_settings.get('max_drug_feat', 1),
        max_cell_feat=input_settings.get('max_cell_feat', 1),
        min_drug_feat=input_settings.get('min_drug_feat', 1),
        min_cell_feat=input_settings.get('min_cell_feat', 1),

        hp_tune=input_settings['hp_tune'],
        rewire_method=input_settings.get('rewire_method', None),
        wandb=input_settings.get('wandb', {}),
        bohb=input_settings.get('bohb', {}),

        input_dir=input_dir,
        out_dir=out_dir,
        split_dir=f"{input_dir}/splits",
        start_run=input_settings.get('start_run', 1),
        end_run=input_settings.get('end_run', 1),
        seeds=input_settings.get('seeds', {}),
        train_type=input_settings.get('train_type', 'regular'),
        use_best_hyperparam=input_settings.get('use_best_hyperparam', False),
        split_type=input_settings.get('split_type', '')
    )

    # Checks
    if params.hp_tune:
        assert params.bohb != {}, "BOHB params required in config for hyperparameter tuning"

    if params.wandb.get('enabled', False):
        assert params.wandb.get('entity_name') is not None, "Entity name required for wandb"
        assert params.wandb.get('token') is not None, "Token required for wandb"

    return inputs, params