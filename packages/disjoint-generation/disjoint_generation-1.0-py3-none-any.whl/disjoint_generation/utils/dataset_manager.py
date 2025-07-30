# Description: Class for keeping track of the original dataset and for postprocessing the generated dataset
# Author: Anton D. Lautrup
# Date: 14-11-2024

import warnings

import numpy as np

from pandas import DataFrame
from typing import Dict, List, Literal

from itertools import product
from sklearn.preprocessing import OrdinalEncoder

def measure_ratio_of_correlations(df: DataFrame, partitions: Dict[str, List[str]]) -> float:
    """ Measure the relative size of the correlation between the disjoint parts of the dataset. """
    corr_matrix = df.corr().abs()
    corr_matrix = corr_matrix.fillna(0)
    np.fill_diagonal(corr_matrix.values, 0)

    interior, exterior = 0, 0
    for (split1, split2) in product(partitions.values(), repeat=2):
        sub_corr = corr_matrix.loc[split1, split2].values

        if split1 == split2:
            interior += np.linalg.norm(sub_corr, ord='fro')
        else:
            exterior += np.linalg.norm(sub_corr, ord='fro')
            
    ratio = exterior / interior
    return ratio

def random_split_columns(dataset: DataFrame, split_ratios: Dict[str, float], random_state: int = None) -> Dict[str, List[str]]:
    """ Randomly split the columns of a dataset into different splits

    Example:
        >>> import pandas as pd
        >>> dataset = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
        >>> split_ratios = {'split1': 2, 'split2': 1}
        >>> result = random_split_columns(dataset, split_ratios, random_state=1)
        >>> sorted(result.keys())
        ['split1', 'split2']
        >>> sorted(result['split1'])
        ['A', 'C']
        >>> sorted(result['split2'])
        ['B']
    """
    # Normalise the split sizes
    divisor = sum(split_ratios.values())
    split_sizes = {split: int(ratio/divisor*len(list(dataset.columns))) for split, ratio in split_ratios.items()}

    # Check if the split sizes are valid
    sum_diff = abs(sum(split_sizes.values()) - dataset.shape[1])
    if sum_diff != 0:
        for i in range(sum_diff):
            split_sizes[list(split_sizes.keys())[i]] += 1
        warnings.warn(f"Split sizes adjusted to {split_sizes}")
    
    # Randomly shuffle the columns
    dataset = dataset.sample(frac=1, axis=1, random_state=random_state)

    # Split the columns
    split_columns = {}
    for split, size in split_sizes.items():
        split_columns[split] = dataset.iloc[:, :size]
        dataset = dataset.iloc[:, size:]

    if dataset.shape[1] > 0:
        raise Exception(f"Remainder {dataset.columns} of columns were not included in any split!")
        
    return {key: list(frame.columns) for key,frame in split_columns.items()}

def correlated_distribute_columns(dataset: DataFrame, num_partitions: int):
    """ Partition the columns into sets based on correlation. Highly correlated items are (as much as possible) 
    placed into *different* partitions, to ensure that the validator models have more to go on.

    Example:
        >>> import pandas as pd
        >>> dataset = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 0, 0], 'C': [2, 4, 6]})
        >>> correlated_distribute_columns(dataset, num_partitions=2)
        {'split0': ['A', 'B'], 'split1': ['C']}
    """
    corr_matrix = dataset.corr().abs()
    corr_matrix = corr_matrix.fillna(0)
    
    partitions = {f'split{i}': [] for i in range(num_partitions)}
    while corr_matrix.shape[0] > 0:
        mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        upper_triangle = corr_matrix.where(mask)

        try:
            max_corr = upper_triangle.stack().idxmax()
        except ValueError:
            # No more nonzero correlations left - assign the remaining features randomly
            remaining_features = corr_matrix.index.tolist()
            for i, feature in enumerate(remaining_features):
                partition = f'split{i % num_partitions}'
                partitions[partition].append(feature)
            break

        # remove the features from the correlation matrix
        corr_matrix = corr_matrix.drop(index=max_corr[0], columns=max_corr[0])
        corr_matrix = corr_matrix.drop(index=max_corr[1], columns=max_corr[1])

        # add the features to two different random partitions
        r = np.random.choice(num_partitions, size=2, replace=False)
        r1 = min(r[0], r[1])
        r2 = max(r[0], r[1])
        partitions[f'split{r1}'].append(max_corr[0])
        partitions[f'split{r2}'].append(max_corr[1])
    
    return partitions

class DataManager:
    """
    A class to manage datasets, splitting, and reverse encoding.

    Attributes:
        original_dataset (DataFrame): The original dataset.
        encoded_dataset_dict (Dict[str, DataFrame]): The dictionary of encoded datasets.
        column_splits (Dict[str, List[str]]): The dictionary of the used column splits.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> dm = DataManager(df, prepared_splits = {'split1': ['A'], 'split2': ['B']}, verbose=False)
        >>> dm.encoded_dataset_dict['split1'].columns.tolist()
        ['A']
        >>> dm.encoded_dataset_dict['split2'].columns.tolist()
        ['B']
        >>> dm2 = DataManager(df, num_automated_splits=2, verbose=False)
    """
    def __init__(self, original_dataset: DataFrame, 
                 prepared_splits: Dict[str, List[str]] = None,
                 automated_splits: Literal['correlated', 'random'] = 'random',
                 num_automated_splits: int = 2,
                 random_state: int = None,
                 verbose: bool = True,
                 ):
        """ Initialize the DataManager with the original dataset and optional prepared splits.

        Args:
            original_dataset (DataFrame): The original dataset.
            prepared_splits (Dict[str, List[str]], optional): A dictionary where keys are split names and values are lists of column names. Defaults to None.
            num_random_splits (int, optional): The number of random splits to generate if prepared_splits is None. Defaults to 2.
        """

        # Convert categorical columns to numbers using OrdinalEncoder
        self.cats_cols = original_dataset.select_dtypes(include=['object']).columns.tolist()
        if len(self.cats_cols) > 0:
            self.cat_encoder = OrdinalEncoder().fit(original_dataset[self.cats_cols])
            original_dataset[self.cats_cols] = self.cat_encoder.transform(original_dataset[self.cats_cols])

        self.original_dataset = original_dataset

        #BUG: If prepared splits is a dictionary, it cannot have two of the same model names
        if prepared_splits is not None:
            if isinstance(list(prepared_splits.values())[0],list):
                self.column_splits = prepared_splits
            else:
                self.column_splits = random_split_columns(original_dataset, {f'split{i}': split for i, split in enumerate(prepared_splits.values())}, random_state=random_state)
        else:
            match automated_splits:
                case 'correlated':
                    self.column_splits = correlated_distribute_columns(original_dataset, num_partitions=num_automated_splits)
                case 'random':
                    self.column_splits = random_split_columns(original_dataset, {f'split{i}': 1 for i in range(num_automated_splits)}, random_state=random_state)
                case _:
                    raise ValueError(f"Unknown automated_splits option: {automated_splits}. Use 'correlated' or 'random'.")
                
        self.encoded_dataset_dict = self._setup_column_splits(self.column_splits)

        ratio = measure_ratio_of_correlations(original_dataset, self.column_splits)
        if verbose: print(f"DataManager: The exterior correlations are {ratio:.2f} times that of the interiors.")
        pass

    def _setup_column_splits(self, prepared_splits: Dict[str, List[str]]) -> Dict[str, DataFrame]:
        """ Setup the column splits based on the prepared splits.

        Args:
            prepared_splits (Dict[str, List[str]]): A dictionary where keys are split names and values are lists of column names.

        Returns:
            Dict[str, DataFrame]: A dictionary where keys are split names and values are the corresponding DataFrames.
        """
        return {str(split): self.original_dataset[columns] for split, columns in prepared_splits.items()}

    def postprocess(self, generated_dataset: DataFrame) -> DataFrame:
        """ Postprocess the generated dataset to match the original dataset's columns.

        Args:
            generated_dataset (DataFrame): The generated dataset.

        Returns:
            DataFrame: The postprocessed dataset.

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            >>> dm = DataManager(df, {'split1': ['A'], 'split2': ['B']}, verbose=False)
            >>> generated_df = pd.DataFrame({'B': [7, 8], 'A': [5, 6]})
            >>> postprocessed_df = dm.postprocess(generated_df)
            >>> postprocessed_df.columns.tolist()
            ['A', 'B']
        """
        generated_dataset = generated_dataset[list(self.original_dataset.columns)]

        if len(self.cats_cols) > 0:
            generated_dataset[self.cats_cols] = self.cat_encoder.inverse_transform(generated_dataset[self.cats_cols])
        return generated_dataset


if __name__ == "__main__":
    import doctest
    doctest.testmod()