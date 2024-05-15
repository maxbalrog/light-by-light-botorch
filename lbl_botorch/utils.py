'''
Utility functions

Author: Maksim Valialshchikov, @maxbalrog (github)
'''
import json
from ax.storage.json_store.encoder import object_to_json
from ax.storage.json_store.decoder import object_from_json
from ax.modelbridge.factory import get_GPEI
import numpy as np


def save_optimization_state(ax_client, save_path, save_model=False):
    ax_client.save_to_json_file(f'{save_path}/experiment.json')


def load_json_object(json_file):
    with open(json_file, 'r') as f:
        obj = json.load(f)
    ax_obj = object_from_json(obj)
    return ax_obj


def get_model_from_experiment(experiment):
    return get_GPEI(experiment, experiment.fetch_data())


def gather_trials_data(ax_client, metric_names=['N_total','N_disc']):
    metrics = ax_client.experiment.fetch_data().df
    trials = ax_client.experiment.trials
    trials_params = {key: trial.arm.parameters for key,trial in trials.items()}
    print(metrics)
    for key in trials_params:
        for metric_name in metric_names:
            condition = (metrics['metric_name'] == metric_name) & (metrics['trial_index'] == key)
            trials_params[key][metric_name] = metrics.loc[condition]['mean'].iloc[0]
        if 'default_yaml' in trials_params[key].keys():
            trials_params[key].pop('default_yaml')
    return trials_params


def get_params_grid(grids):
    n_params = len(grids)
    meshgrid = np.stack(np.meshgrid(*tuple(grids.values())), -1).reshape(-1, n_params)
    return meshgrid

    

