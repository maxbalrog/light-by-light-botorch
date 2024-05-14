'''
Optimization functions

Author: Maksim Valialshchikov, @maxbalrog (github)
'''
import os
import json
import time
import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties
from submitit import AutoExecutor, LocalJob, DebugJob

from light_by_light.utils import read_yaml
from lbl_botorch.evaluate_trial import lbl_evaluation
from lbl_botorch.utils import save_optimization_state, get_params_grid

__all__ = ['run_axclient_optimization', 'run_axclient_optimization_batch']


def run_axclient_optimization(params_yaml):
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


def run_axclient_optimization_batch(params_yaml):
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
        outcome_constraints=params.get('outcome_constraints', None),
    )

    cluster = params.get('cluster', 'slurm')
    executor = AutoExecutor(folder=f"{save_path}/submitit_runs", cluster=cluster)
    executor.update_parameters(**params['sbatch_params'])

    num_parallel_jobs = params.get('num_parallel_jobs', 3)
    
    jobs = []
    submitted_jobs = 0
    # Run until all the jobs have finished and our budget is used up.
    while submitted_jobs < n_trials or jobs:
        for job, trial_idx in jobs[:]:
            # Poll if any jobs completed
            # Local and debug jobs don't run until .result() is called.
            if job.done() or type(job) in [LocalJob, DebugJob]:
                result = job.result()
                ax_client.complete_trial(trial_index=trial_idx, raw_data=result)
                jobs.remove((job, trial_idx))
                ax_client.save_to_json_file(f'{save_path}/experiment.json')
        
        # Schedule new jobs if there is availablity
        trial_index_to_param, _ = ax_client.get_next_trials(
            max_trials=min(num_parallel_jobs - len(jobs), n_trials - submitted_jobs))
        for trial_idx, parameters in trial_index_to_param.items():
            parameters['trial_idx'] = trial_idx
            job = executor.submit(lbl_evaluation, parameters)
            submitted_jobs += 1
            jobs.append((job, trial_idx))
            time.sleep(1)
    print('Optimization finished!')


def run_axclient_gridscan_batch(params_yaml):
    params = read_yaml(params_yaml)
    n_trials = params['n_trials']
    save_path = os.path.dirname(params_yaml)
    objectives = params['objectives']
    default_yaml = params['parameters'][-1]['value']
    
    ax_client = AxClient()
    
    ax_client.create_experiment(
        name=params['name'],
        parameters=params['parameters'],
        objectives={name: ObjectiveProperties(minimize=flag) for name,flag in objectives},
        parameter_constraints=params.get('parameter_constraints', None),
        outcome_constraints=params.get('outcome_constraints', None),
    )

    cluster = params.get('cluster', 'slurm')
    executor = AutoExecutor(folder=f"{save_path}/submitit_runs", cluster=cluster)
    executor.update_parameters(**params['sbatch_params'])

    num_parallel_jobs = params.get('num_parallel_jobs', 3)

    # create a grid over parameters to investigate
    grids = params['grids']
    grid_names = list(grids.keys())
    params_grid = get_params_grid(grids)
    for idx,param in enumerate(params_grid):
        param_dict = {grid_name: p for (grid_name,p) in zip(grid_names, param)}
        param_dict['default_yaml'] = default_yaml
        ax_client.attach_trial(
            parameters=param_dict
        )
    n_trials = params_grid.shape[0]
            
    
    jobs = []
    submitted_jobs = 0
    # Run until all the jobs have finished and our budget is used up.
    while submitted_jobs < n_trials or jobs:
        for job, trial_idx in jobs[:]:
            # Poll if any jobs completed
            # Local and debug jobs don't run until .result() is called.
            if job.done() or type(job) in [LocalJob, DebugJob]:
                result = job.result()
                ax_client.complete_trial(trial_index=trial_idx, raw_data=result)
                jobs.remove((job, trial_idx))
                ax_client.save_to_json_file(f'{save_path}/experiment.json')
        
        # Schedule new jobs if there is availablity
        # trial_index_to_param, _ = ax_client.get_next_trials(
        #     max_trials=min(num_parallel_jobs - len(jobs), n_trials - submitted_jobs))
        n_new_jobs = min(num_parallel_jobs - len(jobs), n_trials - submitted_jobs)
        # for trial_idx, parameters in trial_index_to_param.items():
        for idx in range(n_new_jobs):
            trial_idx = submitted_jobs
            parameters = ax_client.get_trial_parameters(trial_index=trial_idx)
            parameters['trial_idx'] = trial_idx
            job = executor.submit(lbl_evaluation, parameters)
            submitted_jobs += 1
            jobs.append((job, trial_idx))
            time.sleep(1)
    print('Optimization finished!')

