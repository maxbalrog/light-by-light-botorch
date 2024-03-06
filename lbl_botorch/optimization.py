import os
import json
import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties

from light_by_light.utils import read_yaml
from lbl_botorch.evaluate_trial import lbl_evaluation
from lbl_botorch.utils import save_optimization_state


def run_axserver_optimization(params_yaml):
    params = read_yaml(params_yaml)
    n_trials = params['n_trials']
    save_path = os.path.dirname(params_yaml)
    objectives = params['objectives']
    
    ax_client = AxClient()
    
    ax_client.create_experiment(
        name=params['name'],
        parameters=params['parameters'],
        objectives={name: ObjectiveProperties(minimize=flag) for name,flag in objectives},
        parameter_constraints=params.get('parameter_constraints', None),
        outcome_constraints=params.get('outcome_constraints', None),  # Optional.
    )

    for i in range(n_trials):
        parameterization, trial_idx = ax_client.get_next_trial()
        parameterization['trial_idx'] = trial_idx
        ax_client.complete_trial(trial_index=trial_idx,
                                 raw_data=lbl_evaluation(parameterization))
        ax_client.save_to_json_file(f'{save_path}/experiment.json')
    print('Optimization finished!')

