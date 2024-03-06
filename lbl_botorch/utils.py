import json
from ax.storage.json_store.encoder import object_to_json
from ax.storage.json_store.decoder import object_from_json
from ax.modelbridge.factory import get_GPEI


def save_optimization_state(ax_client, save_path, save_model=False):
    ax_client.save_to_json_file(f'{save_path}/experiment.json')


def load_json_object(json_file):
    with open(json_file, 'r') as f:
        obj = json.load(f)
    ax_obj = object_from_json(obj)
    return ax_obj


def get_model_from_experiment(experiment):
    return get_GPEI(experiment, experiment.fetch_data())


