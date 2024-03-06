import numpy as np

from light_by_light.vacem_simulation import run_simulation_postprocess
from light_by_light.utils import read_yaml, write_yaml


def run_trial(simulation_params):
    laser_params = simulation_params['laser_params']
    simulation_params['laser_params'] = list(laser_params.values())
    
    run_simulation_postprocess(**simulation_params)
    
    path = simulation_params['save_path']
    data = np.load(f'{path}postprocess_data.npz')
    return data


def lbl_evaluation(parameterization):
    default_params = read_yaml(parameterization['default_yaml'])
    save_path = default_params['save_path']
    trial_idx = parameterization['trial_idx']
    print(parameterization)
    parameterization.pop('default_yaml', None)
    parameterization.pop('trial_idx', None)

    trial_str = str(trial_idx).zfill(3)
    default_params['save_path'] = f'{save_path}trial_{trial_str}/'
    
    # extract all parameterization items
    for key,value in parameterization.items():
        if 'laser' in key:
            laser, param = key.split('/')
            default_params['laser_params'][laser][param] = value
        elif 'box_factors' in key or 'resolutions' in key:
            sim, param = key.split('/')
            default_params['simbox_params'][sim][param] = value
    
    data = run_trial(default_params)
    metrics = {'N_disc': (float(data['N_disc_num']), 0.0),
               'N_total': (float(data['N_total']), 0.0),
               'energy': (float(data['energy_num']), 0.0)}
    return metrics
    