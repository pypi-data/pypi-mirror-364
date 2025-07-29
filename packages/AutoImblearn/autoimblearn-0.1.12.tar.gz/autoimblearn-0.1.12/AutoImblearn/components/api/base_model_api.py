import os
import logging
from abc import ABC, abstractmethod
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from types import SimpleNamespace

class Arguments:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

class BaseModelAPI(ABC):
    def __init__(self, import_name):
        self.app = Flask(import_name)
        self.params = {}
        self.result = None

        # Register routes
        self.app.add_url_rule('/set', view_func=self.set_params, methods=['POST'])
        self.app.add_url_rule('/train/<dataset_name>', view_func=self.train, methods=['GET'])
        self.app.add_url_rule('/health', view_func=self.health, methods=['GET'])
        self.app.add_url_rule('/predict', view_func=self.get_result, methods=['POST'])
        self.app.add_url_rule('/hyperparameters', view_func=self.get_hyperparameters(), methods=['GET'])


    def get_hyperparameters(self):
        return jsonify(self.get_hyperparameter_search_space())

    @abstractmethod
    def get_hyperparameter_search_space(self) -> dict:
        # Returns a dictionary that defines the hyperparameters and their ranges/types.
        pass

    def dict_to_namespace(self):
        # Parse dict object to python class attributes like object
        def recurse(d):
            ns = {}
            for k, v in d.items():
                if isinstance(v, dict) and "default" in v:
                    ns[k] = v["default"]
                elif isinstance(v, dict):
                    ns[k] = recurse(v)
                else:
                    ns[k] = v  # fallback
            return SimpleNamespace(**ns)
        return recurse(self.params)

    def health(self):
        return "OK", 200

    def set_params(self):
        """Set training parameters"""
        def recursive_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and isinstance(d.get(k), dict):
                    recursive_update(d[k], v)
                else:
                    d[k] = v

        data = request.get_json()

        # TODO delete
        print(data)

        recursive_update(self.params, data)

        if 'metric' not in self.params:
        # if 'metric' not in self.params
                raise Exception("data not complete, need to include metric")
        return jsonify(self.params), 201

    @abstractmethod
    def fit_train(self, args, X_train, y_train, X_test, y_test):
        """Control the actual model training process"""
        pass

    def train(self, dataset_name: str):
        """Load data, run training, and return result"""
        args = Arguments(self.params)

        X_train = pd.read_csv(os.path.join("/data/interim", args.data_names[0])).to_numpy()
        y_train = pd.read_csv(os.path.join("/data/interim", args.data_names[1])).to_numpy().ravel()
        X_test = pd.read_csv(os.path.join("/data/interim", args.data_names[2])).to_numpy()
        y_test = pd.read_csv(os.path.join("/data/interim", args.data_names[3])).to_numpy().ravel()
        logging.info("loading finished")

        self.result = self.fit_train(args, X_train, y_train, X_test, y_test)
        logging.info("finished training")
        return {}, 200
        # return jsonify({"result": self.result}), 200

    def get_result(self):
        return jsonify({"result": self.result}), 200

    def run(self, host='0.0.0.0', port=8080, debug=True):
        self.app.run(host=host, port=port, debug=debug)
