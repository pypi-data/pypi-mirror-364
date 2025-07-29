import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

class DistributionDescriptors:
    """
    A class to represent the distribution descriptors of a single variable.
    """

    def __init__(self, column: pd.Series=None, json_data: dict=None):
        """
        Initializes the DistributionDescriptors from a pandas Series or a JSON representation.
        """
        if column is not None:
            self.mean = column.mean()
            self.std = column.std()
            self.min_val = column.min()
            self.max_val = column.max()
            self.q1 = column.quantile(0.25)
            self.q2 = column.quantile(0.5)
            self.q3 = column.quantile(0.75)
        elif json_data is not None:
            self.mean = json_data['mean']
            self.std = json_data['std']
            self.min_val = json_data['min_val']
            self.max_val = json_data['max_val']
            self.q1 = json_data['q1']
            self.q2 = json_data['q2']
            self.q3 = json_data['q3']
        else:
            raise ValueError("Either a pandas Series or JSON data must be provided to initialize DistributionDescriptors.")        

    def __repr__(self):
        """
        Returns a string representation of the DistributionDescriptors.
        """
        return (f"DistributionDescriptors(mean={self.mean}, std={self.std}, "
                f"min_val={self.min_val}, max_val={self.max_val}, "
                f"q1={self.q1}, q2={self.q2}, q3={self.q3})")
    
    def get_json(self) -> dict:
        """
        Returns a JSON representation of the DistributionDescriptors.
        """
        return {
            "mean": self.mean,
            "std": self.std,
            "min_val": self.min_val,
            "max_val": self.max_val,
            "q1": self.q1,
            "q2": self.q2,
            "q3": self.q3
        }
    
    def __eq__(self, value):
        if not isinstance(value, DistributionDescriptors):
            return NotImplemented

        return (self.mean == value.mean and
                self.std == value.std and
                self.min_val == value.min_val and
                self.max_val == value.max_val and
                self.q1 == value.q1 and
                self.q2 == value.q2 and
                self.q3 == value.q3)

class DistributionChanges:
    """
    A class to represent the changes in distribution between two variables.
    """

    def __init__(self, original: DistributionDescriptors, new_data: DistributionDescriptors, sigma: float = 1.0, delta: float = 0.1):
        """
        Initializes the DistributionChanges with descriptors from two distributions.
        """
        self.original = original
        self.new_data = new_data
        self.sigma = sigma
        self.delta = delta

        self.changed = dict()
        self.unchanged = dict()
        
        metrics = [
            ("mean", original.mean, new_data.mean, sigma * original.std),
            ("std", original.std, new_data.std, delta * original.std),
            ("q1", original.q1, new_data.q1, delta * original.q1),
            ("q2", original.q2, new_data.q2, delta * original.q2),
            ("q3", original.q3, new_data.q3, delta * original.q3),
        ]

        for name, orig_val, new_val, threshold in metrics:
            diff = abs(orig_val - new_val)
            # Avoid division by zero
            if threshold == 0:
                percentage_diff = 0
            else:
                percentage_diff = diff / abs(threshold)
                if diff > abs(threshold):
                    self.changed[name] = int(percentage_diff * 100)
                else:
                    self.unchanged[name] = int(percentage_diff * 100)

    def __repr__(self):
        """
        Returns a string representation of the DistributionChanges.
        """
        change_str = ', '.join([f"{k}: {v}%" for k, v in self.changed.items()])
        unchanged_str = ', '.join([f"{k}: {v}%" for k, v in self.unchanged.items()])

        return f"Changes: {change_str}, Unchanged: {unchanged_str}, Sigma: {self.sigma}, Delta: {self.delta}"
    
    def get_json(self) -> dict:
        """
        Returns a JSON representation of the DistributionChanges.
        """
        return {
            "changed": self.changed,
            "unchanged": self.unchanged,
            "sigma": self.sigma,
            "delta": self.delta,
        }

def get_distribution_descriptors(column: pd.Series) -> DistributionDescriptors:
    """
    Returns the distribution descriptors of a given column in a pandas DataFrame.

    Parameters:
    column (pd.Series): The column for which to calculate the distribution descriptors.
    """
    return DistributionDescriptors(column)

def get_distribution_descriptors_from_json(json_data: dict) -> DistributionDescriptors:
    """
    Returns the distribution descriptors from a JSON representation.
    """
    return {column: DistributionDescriptors(json_data=column_data) for column, column_data in json_data.items()}

def get_distribution_descriptors_all_columns(df: pd.DataFrame) -> dict[str, DistributionDescriptors]:
    """
    Returns the distribution descriptors for all columns in a pandas DataFrame.
    """
    return {col: get_distribution_descriptors(df[col]) for col in df.columns}

def _generate_distribution(column: pd.Series):
    """
    Generates a distribution of the data in the column using little balls.
    This function is used internally to plot the distribution of the data.
    """
    _, bins = pd.cut(column, bins=20, retbins=True)
    y_pos = np.zeros(len(column))
    max_pos_bin = np.array([0]*(len(bins)-1))

    for i, data_entry in enumerate(column):
        bin_pos = np.digitize(data_entry, bins)
        # Ensure bin_pos is within valid range
        bin_pos = min(max(bin_pos, 0), len(max_pos_bin) - 1)
        y_pos[i] = max_pos_bin[bin_pos]
        max_pos_bin[bin_pos] += 1

    return y_pos

def plot_distribution_descriptors(column: pd.Series, ax: plt.Axes = None, path: str = None, show: bool = True):
    """
    Plots the distribution descriptors using matplotlib and returns the figure.
    """
    descriptors = get_distribution_descriptors(column)
    if ax is None:
        ax = plt.subplots(figsize=(8, 4))[1]
    y_pos = _generate_distribution(column)

    ax.axvline(descriptors.mean, color='red', linestyle='-', linewidth=2, label=f'Mean: {descriptors.mean:.2f}')
    ax.axvline(descriptors.q1, color='green', linestyle='-', linewidth=2, label=f'Q1: {descriptors.q1:.2f}')
    ax.axvline(descriptors.q2, color='orange', linestyle='-', linewidth=2, label=f'Median (Q2): {descriptors.q2:.2f}')
    ax.axvline(descriptors.q3, color='purple', linestyle='-', linewidth=2, label=f'Q3: {descriptors.q3:.2f}')
    ax.axvline(descriptors.min_val, color='brown', linestyle='-', linewidth=2, label=f'Min: {descriptors.min_val:.2f}')
    ax.axvline(descriptors.max_val, color='pink', linestyle='-', linewidth=2, label=f'Max: {descriptors.max_val:.2f}')
    ax.legend()

    ax.scatter(column, y_pos, s=30, color='blue', alpha=0.6, edgecolors='black')
    ax.set_title(f'Distribution of {column.name}')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency (balls)')

    if show:
        plt.show()
    
def plot_distribution_descriptors_all_columns(df: pd.DataFrame, path: str = None):
    """
    Plots the distribution descriptors for all columns in a pandas DataFrame.
    """

    fig, axes = plt.subplots(nrows=len(df.columns), ncols=1, figsize=(10, 5 * len(df.columns)))
    for i, col in enumerate(df.columns):
        plot_distribution_descriptors(df[col], ax=axes[i], show=False)
        axes[i].set_title(f'Distribution of {col}')

    plt.tight_layout()

    if path:
        os.makedirs(path, exist_ok=True)
        plt.savefig(f"{path}/distribution_descriptors_all_columns.png")
        plt.close()
    else:
        plt.show()

def compare_distributions(original: pd.Series, new_data: pd.Series, sigma: float = 1.0, delta: float = 0.1, name: str = None, path: str = None) -> DistributionChanges:
    """
    Compares the distributions of two columns in a pandas series.
    """
    changes = DistributionChanges(
        original=get_distribution_descriptors(original),
        new_data=get_distribution_descriptors(new_data),
        sigma=sigma,
        delta=delta
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 4))
    fig.suptitle(f"Distribution Comparison: {name if name else 'Unnamed'}")
    if path:
        plot_distribution_descriptors(original, axes[0], show=False)
    axes[0].set_title('Original Distribution')

    if path:
        plot_distribution_descriptors(new_data, axes[1], show=False)
    axes[1].set_title('New Data Distribution')

    plt.tight_layout()
    
    if path:
        os.makedirs(path, exist_ok=True)
        plt.savefig(f"{path}/distribution_comparison_{name if name else 'unnamed'}.png")
        plt.close()
    else:
        plt.show()

    return changes 

def compare_distribbutions_all_columns(original: pd.DataFrame, new_data: pd.DataFrame, sigma: float = 1.0, delta: float = 0.1, path: str = None):
    """
    Compares the distributions of all columns in two pandas DataFrames.
    """
    result = {}
    for column_name in original.columns:
        original_series = original[column_name]
        new_data_series = new_data[column_name]
        changes = compare_distributions(original_series, new_data_series, sigma=sigma, delta=delta, name=column_name, path=path)
        if path is None:
            print(f"Changes in column '{column_name}': {changes}")
        result[column_name] = changes.get_json()

    return result

def descriptor_evolution(dfs: list[pd.Series], name: str = None, path: str = None):
    """
    Compares the evolution of descriptors across different DataFrames.
    """

    descriptors = [get_distribution_descriptors(df) for df in dfs]

    plt.figure(figsize=(10, 6))
    plt.suptitle(f"Evolution of {name}")

    for i, (title, values, ylabel) in enumerate([
        ('Mean Evolution', [d.mean for d in descriptors], 'Mean'),
        ('Standard Deviation Evolution', [d.std for d in descriptors], 'Standard Deviation'),
        ('Q1 Evolution', [d.q1 for d in descriptors], 'Q1'),
        ('Q2 Evolution', [d.q2 for d in descriptors], 'Q2'),
        ('Q3 Evolution', [d.q3 for d in descriptors], 'Q3')
    ], 1):
        plt.subplot(2, 3, i)
        plt.plot(values, marker='o', linestyle='-', label=title)
        plt.title(title)
        plt.xlabel('Index')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout(pad=2.0)

    if path:
        os.makedirs(path, exist_ok=True)
        plt.savefig(f"{path}/descriptor_evolution_{name if name else 'unnamed'}.png")
        plt.close()
    else:
        plt.show()

def descriptor_evolution_all_columns(dfs: list[pd.DataFrame], path: str = None):
    """
    Compares the evolution of descriptors across different DataFrames.
    """
    for column_name in dfs[0].columns:
        series_list = [df[column_name] for df in dfs]
        descriptor_evolution(series_list, name=column_name, path=path)
    
