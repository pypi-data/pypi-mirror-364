# Description: Script for generating synthetic datasets in a variety of ways
# Author: Anton D. Lautrup
# Date: 18-11-2024

import os
import subprocess

import numpy as np
import pandas as pd

from typing import List
from pandas import DataFrame
from abc import ABC, abstractmethod

from synthcity.plugins import Plugins

from DataSynthesizer.DataDescriber import DataDescriber
from DataSynthesizer.DataGenerator import DataGenerator

def _load_data(file_name: str) -> DataFrame:
    df_train = pd.read_csv(file_name + '.csv').dropna()
    return df_train

def _write_data(df: DataFrame, file_name: str) -> None:
    df.to_csv(file_name, index=False)

def _cleanup_files(file_names: List[str]) -> None:
    for file_name in file_names:
        if os.path.exists(file_name):
            os.remove(file_name)
    pass

class DataGeneratorAdapter(ABC):
    """ Abstract class for data generator adapters.

    Required Methods:
        generate(train_data_name: str | DataFrame, num_to_generate: int = None, id: int = 0) -> DataFrame: Generate synthetic data.
    """
    def __str__(self):
        return f"{self.name}"

    @abstractmethod
    def generate(self, train_data_name: str | DataFrame, num_to_generate: int = None, seed: int = None, id = 0, **kwargs) -> DataFrame:
        """ Generate synthetic data based on the training data.

        Args:
            train_data_name (str): The name of the training data file.

        Returns:
            DataFrame: The generated synthetic data.
        """
        pass

class SynthCityAdapter(DataGeneratorAdapter):
    """ SynthCity Adapter for generating synthetic data.

    Attributes:
        gen_model (str): The generative model to use.
    """
    def __init__(self, gen_model):
        self.gen_model = gen_model

    def generate(self, train_data: str | DataFrame, num_to_generate: int = None, seed: int = None, id = 0, **kwargs) -> DataFrame:
        """ Generate synthetic data using SynthCity.

        Reference:
            Qian, Z., Cebere, B.-C., & van der Schaar, M. (2023). Synthcity: facilitating innovative 
            use cases of synthetic data in different data modalities. http://arxiv.org/abs/2301.07573

        Args:
            train_data (str, DataFrame): The name of the training data file or the DataFrame.
            num_to_generate (int): The number of synthetic data points to generate.

        Returns:
            DataFrame: The generated synthetic data.

        Example:
            >>> adapter = SynthCityAdapter('privbayes')
            >>> df_syn = adapter.generate('tests/dummy_train') # doctest: +ELLIPSIS
            >>> isinstance(df_syn, pd.DataFrame)
            True
        """
        
        if isinstance(train_data, str):
            df_train = _load_data(train_data)
        else:
            df_train = train_data

        if seed is None: seed = np.random.randint(0, 1000000)
        syn_model = Plugins().get(self.gen_model, random_state = seed, **kwargs)
        syn_model.fit(df_train)

        if num_to_generate is None: num_to_generate = len(df_train)
        df_syn = syn_model.generate(count=num_to_generate).dataframe()

        ## Sometimes the model does not generate enough samples (i.e., small categorical subsets have duplicates removed)
        if len(df_syn) < num_to_generate:
            df_mis = syn_model.generate(count=num_to_generate-len(df_syn)).dataframe()
            df_syn = pd.concat([df_syn, df_mis], ignore_index=True)

        if len(df_syn) < num_to_generate:
            print(f"Warning: {num_to_generate-len(df_syn)} missing samples. Re-sampling to fill.")
            df_mis = df_syn.sample(n=num_to_generate-len(df_syn), replace=True)
            df_syn = pd.concat([df_syn, df_mis], ignore_index=True)

        return df_syn[:num_to_generate]

from importlib.resources import files
class SynthPopAdapter(DataGeneratorAdapter):
    def generate(self, train_data: str | DataFrame, num_to_generate: int = None, seed: int = None, id = 0,  **kwargs) -> DataFrame:
        """ Generate synthetic data using SynthPop in R using subprocess.
        Be sure to check that R is installed and Rscript is a valid command in the terminal.

        Reference:
            Nowok, B., Raab, G. M., & Dibben, C. (2016). synthpop: Bespoke Creation of Synthetic Data in R. 
            Journal of Statistical Software, 74(11), 1--26. https://doi.org/10.18637/jss.v074.i11

        Args:
            train_data (str, DataFrame): The name of the training data file or the DataFrame.
            num_to_generate (int): The number of synthetic data points to generate.

        Returns:
            DataFrame: The generated synthetic data.

        Example:
            >>> adapter = SynthPopAdapter()
            >>> df_syn = adapter.generate('tests/dummy_train') # doctest: +SKIP
            >>> isinstance(df_syn, pd.DataFrame) # doctest: +SKIP
            True
        """
        # if self.r_access == 'subprocess':

        if isinstance(train_data, str):
            train_data_name = train_data
        else:
            train_data_name = f'synthpop_temp_{id}'
            _write_data(train_data, train_data_name + '.csv')

        df_train = _load_data(train_data_name)

        info_dir = 'synthesis_info_' + train_data_name.split('/')[0]
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)

        r_script_path = files('disjoint_generation').joinpath('utils/subprocess/synthpop_subprocess.R')
        command = [
                    "Rscript",
                    str(r_script_path),
                    train_data_name +".csv",
                    train_data_name + "_synthpop",
                    str(num_to_generate) if num_to_generate is not None else str(len(df_train)),
                    str(seed) if seed is not None else "",
                ]
        subprocess.run(command, check=True)

        df_syn = pd.read_csv(train_data_name + '_synthpop.csv')
        df_syn.columns = [col for col in df_train.columns]

        _cleanup_files(['synthesis_info_' + train_data_name + '_synthpop.txt', 
                        train_data_name + '_synthpop.csv', 
                        f'synthpop_temp_{id}.csv'])

        os.removedirs(info_dir)
        return df_syn

class DataSynthesizerAdapter(DataGeneratorAdapter):
    """ DataSynthesizer Adapter for generating synthetic data.

    Attributes:
        epsilon (float): The privacy parameter epsilon for differential privacy (0 is turned off).
    """
    def __init__(self, epsilon: float = 0):
        self.epsilon = epsilon

    def generate(self, train_data: str | DataFrame, num_to_generate: int = None, seed: int = None, id = 0, **kwargs) -> DataFrame:
        """ Generate synthetic data using DataSynthesizer.

        Reference:
            Ping, H., Stoyanovich, J., & Howe, B. 2017. DataSynthesizer: Privacy-Preserving Synthetic Datasets. 
            In Proceedings of the 29th International Conference on Scientific and Statistical Database Management (SSDBM '17). 
            Association for Computing Machinery, New York, NY, USA, Article 42, 1--5. https://doi.org/10.1145/3085504.3091117

        Args:
            train_data (str, DataFrame): The name of the training data file or the DataFrame.
            num_to_generate (int): The number of synthetic data points to generate.

        Returns:
            DataFrame: The generated synthetic data.

        Example:
            >>> adapter = DataSynthesizerAdapter()
            >>> df_syn = adapter.generate('tests/dummy_train') # doctest: +ELLIPSIS
            -etc-
            >>> isinstance(df_syn, pd.DataFrame)
            True
        """

        if isinstance(train_data, str):
            train_data_name = train_data
        else:
            train_data_name = f'datasynthesizer_temp_{id}'
            _write_data(train_data, train_data_name + '.csv')
        
        df_train = _load_data(train_data_name)

        description_file = train_data_name + f"_datasynthesizer_{id}_info.json"

        describer = DataDescriber(category_threshold=10)
        describer.describe_dataset_in_correlated_attribute_mode(dataset_file = train_data_name +'.csv', 
                                                                epsilon=self.epsilon, 
                                                                k=2,
                                                                attribute_to_is_categorical={},
                                                                seed = seed
                                                                )
        describer.save_dataset_description_to_file(description_file)

        generator = DataGenerator()

        if num_to_generate is None: num_to_generate = len(df_train)
        generator.generate_dataset_in_correlated_attribute_mode(num_to_generate, description_file, seed = seed)

        df_syn = generator.synthetic_dataset

        _cleanup_files([description_file, f'datasynthesizer_temp_{id}.csv'])

        return df_syn

class DebugAdapter(DataGeneratorAdapter):
    def generate(self, train_data: str | DataFrame, num_to_generate: int = None, seed: int = None, id = 0, **kwargs) -> DataFrame:
        if isinstance(train_data, str):
            train_data = _load_data(train_data)
        return train_data

def generate_synthetic_data(train_data: DataFrame | str, gen_model: str, num_to_generate: int = None, seed: int = None, id = 0, **kwargs) -> DataFrame:
    """ Generate synthetic data using the specified generative model.

    Args:
        train_data (DataFrame, str): The training data DataFrame or filename.
        gen_model (str): The name of the generative model.
        id (int): instance index (to prevent overwriting files for parallel runs).
        num_to_generate (int): The number of synthetic data points to generate.

    Returns:
        DataFrame: The generated synthetic data.

    Example:
        >>> df_syn = generate_synthetic_data('tests/dummy_train', 'privbayes')
        >>> isinstance(df_syn, pd.DataFrame)
        True
    """
    # TODO: stop instantiating all adapters every time
    adapters = {
        'ctgan': SynthCityAdapter(gen_model),
        'adsgan': SynthCityAdapter(gen_model),
        'tvae': SynthCityAdapter(gen_model),
        'nflow': SynthCityAdapter(gen_model),
        'ddpm': SynthCityAdapter(gen_model),
        'dpgan': SynthCityAdapter(gen_model),
        'privbayes': SynthCityAdapter(gen_model),
        'synthpop': SynthPopAdapter(),
        'datasynthesizer': DataSynthesizerAdapter(),
        'datasynthesizer-dp': DataSynthesizerAdapter(epsilon=0.1),
        'debug': DebugAdapter()
    }

    if gen_model in adapters:
        adapter = adapters[gen_model]
        df_syn = adapter.generate(train_data, num_to_generate, seed, id, **kwargs)
    elif isinstance(gen_model, DataGeneratorAdapter):
        df_syn = gen_model.generate(train_data, num_to_generate, seed, id, **kwargs)
    else:
        raise NotImplementedError("The chosen generative model could not be run!")
    return df_syn


if __name__ == "__main__":
    import doctest
    doctest.ELLIPSIS_MARKER = '-etc-'
    doctest.testmod()