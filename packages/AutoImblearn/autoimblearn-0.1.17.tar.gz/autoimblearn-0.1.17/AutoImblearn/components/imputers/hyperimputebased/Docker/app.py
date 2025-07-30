from AutoImblearn.components.api import BaseTransformerAPI
import logging
import numpy as np


class RunAutosmoteAPI(BaseTransformerAPI):
    def get_hyperparameter_search_space(self):
        return {
        }


    def fit(self, args, X_train, y_train, X_test, y_test):
        params = self.dict_to_namespace()
        params.metric = args.metric

        size = X_train.shape[0]
        indices = np.arange(size)
        np.random.shuffle(indices)

        val_idx = indices[:int(size * args.val_ratio)]
        train_idx = indices[int(size * args.val_ratio):]

        train_X, val_X = X_train[train_idx], X_train[val_idx]
        train_y, val_y = y_train[train_idx], y_train[val_idx]

        logging.info("finished parameter setting")

        params.ratio_map = [0.0, 0.25, 0.5, 0.75, 1.0]
        clf = get_clf(params.clf)
        return train(params, train_X, train_y, val_X, val_y, X_test, y_test, clf)

    def transform(self, X):
        return X
