# Description: Disjoint Generative Model Manager Class
# Author: Anton D. Lautrup
# Date: 14-11-2024
# Version: 0.1.0
# License: MIT

from pandas import DataFrame
from typing import Dict, List, Literal

from joblib import Parallel, delayed

from .utils.dataset_manager import DataManager
from .utils.generative_model_adapters import DataGeneratorAdapter
from .utils.joining_strategies import JoinStrategy, Concatenating, UsingJoiningValidator

from .utils.generative_model_adapters import generate_synthetic_data


class DisjointGenerativeModels:
    """ Class for managing disjoint generative models.

    Attributes:
        original_data (DataFrame): The original (training) data.
        training_data (Dict[str, DataFrame]): The training data, split into different splits.
        generative_models (List[str]): The generative models to use.
        used_splits (Dict[str, List[str]]): The divisions of columns actually used.
        worker_id (int): The worker id for parallel runs.
        synthetic_data (DataFrame): The synthetic data (once generated).
        join_multiplier (int): The multiplier for the number of samples to generate (for using join validator).
    """
    def __init__(self,
                 training_data,
                 generative_models: List[str | DataGeneratorAdapter] | Dict[str | DataGeneratorAdapter, List[str]],
                 prepared_splits: Dict[str, List[str]] | Literal['correlated', 'random'] = None,
                 joining_strategy: JoinStrategy = UsingJoiningValidator(),
                 random_state: int = None,
                 parallel_worker_id: int = 0,
                 ):
        """ Initialize the DisjointGenerativeModels class.

        Args:
            training_data (DataFrame): The training data (before splitting).
            generative_models (List[str | DataGeneratorAdapter] | Dict[str | DataGeneratorAdapter, List[str]]): The generative models to use (can add column name lists).
            prepared_splits (Dict[str, List[str]]): Predefined splits of columns, if none use random splits for each model.
            joining_strategy (JoinStrategy): The strategy for joining dataframes, defaults to using joining validator.
            random_state (int): Random seed used for the generative models and joining process (note that it does not gurantee 100% reproducible results).
            parallel_worker_id (int): Index for not overwriting files in parallel runs.
        """
        self.original_data = training_data
        self.generative_models = generative_models
        self.used_splits = prepared_splits

        self.random_state = random_state
        self.worker_id = parallel_worker_id

        self._strategy = joining_strategy
        self.join_multiplier = 3
        pass
    
    @property
    def strategy(self) -> JoinStrategy:
        """ Get the current strategy for joining dataframes."""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: JoinStrategy) -> None:
        """ Change the current strategy for joining dataframes."""
        self._strategy = strategy

    def _setup(self):
        """ Perform the initial setup of the data and models."""
        
        split_kwargs = {'prepared_splits': self.used_splits}
        if self.used_splits is None:
            if isinstance(self.generative_models, Dict):
                split_kwargs = {'prepared_splits': self.generative_models}
        elif self.used_splits == 'correlated':
            split_kwargs = {'automated_splits': 'correlated', 'num_automated_splits': len(self.generative_models)}
        else: # self.used_splits == 'random' or None
            split_kwargs = {'automated_splits': 'random', 'num_automated_splits': len(self.generative_models)}

        self.dm = DataManager(self.original_data.copy(), **split_kwargs)
        
        self.training_data = self.dm.encoded_dataset_dict
        self.used_splits = self.dm.column_splits

        if self.num_samples is None:
            self.num_samples = len(self.original_data)

        if hasattr(self._strategy, 'join_validator'):
            if self._strategy.join_validator.pre_fit is False:
                self._strategy.join_validator.fit_classifier(self.training_data, num_batches_of_bad_joins=2)
                self._strategy.join_validator.pre_fit = True
            self._strategy.max_size = int(self.num_samples)
            self.num_samples = int(self.join_multiplier*self.num_samples)   # multiplier of three seems to do well enough

        if isinstance(self.generative_models, Dict):     # get model names from dict to list
            self.generative_models = list(self.generative_models.keys())
        pass

    def _make_calibration_plot(self, holdout_data: DataFrame, stats: bool = True, save: bool = True) -> None:
        """ Make calibration plots for the validator model fit quality"""
        assert hasattr(self._strategy, 'join_validator'), "No validator model found."

        from .utils.plots import plot_calibration_curve

        dm_temp = DataManager(holdout_data, self.used_splits, verbose=False)
        enc_data = dm_temp.encoded_dataset_dict

        plot_calibration_curve(self._strategy.join_validator, self.training_data, enc_data, stats = stats, save_dir='plots', save_fig = save)
        pass

    def _make_pred_pointplot(self, holdout_data: DataFrame, save: bool = True) -> None:
        """ Make prediction point plots for the validator model fit quality"""
        assert hasattr(self._strategy, 'join_validator'), "No validator model found."

        from .utils.plots import plot_samplespace_distribution

        dm_temp = DataManager(holdout_data, self.used_splits, verbose=False)
        enc_data = dm_temp.encoded_dataset_dict

        plot_samplespace_distribution(self._strategy.join_validator, self.training_data, enc_data, save_dir='plots', save_fig = save)
        pass

    def _evaluate_splits(self):
        # TODO: Calculate fraction of identical rows between joined data and reference data
        # TODO: Calculate record number difference between joined data and reference data
        # TODO: Calculate some other metrics
        pass

    # TODO: split into fit and generate functions
    # TODO: add feature for saving and loading models
    def fit_generate(self, num_samples: int = None, args: Dict[str, any] = {}) -> DataFrame:
        """ Fit the generative models to the training data and generate synthetic data.
        
        Args:
            num_samples (int): The number of samples to generate (defaults to len(train_data)).
            args (Dict[str, any]): Additional arguments to pass to the generative models.

        Returns:
            DataFrame: The synthetic data.

        Example:
            >>> import pandas as pd
            >>> df = pd.read_csv('tests/dummy_train.csv')
            >>> dgm = DisjointGenerativeModels(df, ['privbayes', 'privbayes'], joining_strategy=Concatenating())
            >>> dgm.fit_generate() # doctest: +ELLIPSIS
            -etc-
        """
        self.num_samples = num_samples
        self._setup()

        syn_dfs_dict = {}
        res = Parallel(n_jobs=-1)(delayed(generate_synthetic_data)(train_data, model, num_to_generate=self.num_samples, seed=self.random_state, id=idx+self.worker_id, **args) for idx, model, train_data in zip(range(len(self.generative_models)),self.generative_models, self.training_data.values()))
        syn_dfs_dict = {split_name: df_syn for split_name, df_syn in zip(self.training_data.keys(), res)}
        self.synthetic_data_partitions = syn_dfs_dict

        synthetic_data = self.conduct_joining(syn_dfs_dict)
        
        self.synthetic_data = self.dm.postprocess(synthetic_data)

        return self.synthetic_data

    def conduct_joining(self, data: Dict[str, DataFrame] = None) -> DataFrame:
        """ Perform the joining of dataframes using the current strategy.
        
        Args:
            data (Dict[str, DataFrame]): The data to join.
        
        Returns:
            DataFrame: The joined data.

        Example:
            >>> import pandas as pd
            >>> dict = {'split1': pd.DataFrame({'A': [1, 2], 'B': [3, 4]}), 'split2': pd.DataFrame({'C': [5, 6], 'D': [7, 8]})}
            >>> dgm = DisjointGenerativeModels(None, None, None, Concatenating())
            >>> dgm.conduct_joining(dict) # doctest: +NORMALIZE_WHITESPACE
               A  B  C  D
            0  1  3  5  7
            1  2  4  6  8
        """
        if self._strategy is None:
            self.strategy = Concatenating()

        data = data if data is not None else self.synthetic_data_partitions.copy()
        
        try:
            return self._strategy.join(data.copy())
        except Exception as e:
            print(f"Error in joining data: {e}")

if __name__ == "__main__":
    import doctest
    doctest.ELLIPSIS_MARKER = '-etc-'
    doctest.testmod()