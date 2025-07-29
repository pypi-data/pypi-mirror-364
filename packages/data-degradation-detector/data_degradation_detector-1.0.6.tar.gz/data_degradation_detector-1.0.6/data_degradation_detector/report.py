import pandas as pd
from . import univariate as uv
from . import multivariate as mv
import json
import os
import matplotlib.pyplot as plt

def get_number_of_output_classes(y: pd.Series) -> int:
    """
    Determine the number of output classes in the Series.
    This function assumes that the Series is the target variable.
    """

    num_classes = len(y.unique())
    return num_classes if num_classes<=10 else None

def create_initial_report(df: pd.DataFrame, base_metrics: dict, path: str, number_of_output_classes: int = None) -> None:
    """
    Create the initial informative visualizations and statistics for the given DataFrame.
    """
    # Get distribution descriptors for all columns
    descriptors = uv.get_distribution_descriptors_all_columns(df)
    descriptors = {k: v.get_json() for k, v in descriptors.items()}

    os.makedirs(path, exist_ok=True)
    with open(f"{path}/base_metrics.json", 'w') as f:
        json.dump(base_metrics, f, indent=4)

    with open(f"{path}/distribution_descriptors.json", 'w') as f:
        json.dump(descriptors, f, indent=4)

    # Plot distribution descriptors for all columns
    uv.plot_distribution_descriptors_all_columns(df, path=path)

    if number_of_output_classes is not None:
        cluster_info = mv.get_cluster_defined_number(df, number_of_output_classes, path=path)
    else:
        cluster_info = mv.get_best_clusters(df, path=path)

    with open(f"{path}/kmeans_clusters.json", 'w+') as f:
        json.dump(cluster_info.get_json(), f, indent=4)

    mv.correlation_matrix(df, path=path)

def create_report(original_df: pd.DataFrame, original_clusters: mv.Cluster_statistics, degraded_dfs: list[pd.DataFrame], base_metrics: dict, path: str, new_metrics: list[dict] = None) -> None:
    """
    Create a report comparing the original and degraded DataFrames.
    """
    for i, degraded_df in enumerate(degraded_dfs):
        degraded_path = f"{path}/degraded_{i}"
        distribution_comparison = uv.compare_distribbutions_all_columns(original_df, degraded_df, path=degraded_path)
        with open(f"{degraded_path}/distribution_comparison_{i}.json", 'w') as f:
            json.dump(distribution_comparison, f, indent=4)

    evolution_path = f"{path}/evolution"
    uv.descriptor_evolution_all_columns(degraded_dfs, path=evolution_path)

    cluster_path = f"{path}/clusters"
    os.makedirs(cluster_path, exist_ok=True)
    degraded_clusters = [mv.get_cluster_defined_number(df, original_clusters.num_clusters, plot=False) for df in degraded_dfs]
    for i, degraded_cluster in enumerate(degraded_clusters):
        cluster_comparison = mv.compare_clusters(original_clusters, degraded_cluster)
        with open(f"{cluster_path}/cluster_comparison_{i}.json", 'w') as f:
            json.dump(cluster_comparison.get_json(), f, indent=4)

    mv.clustering_evolution(degraded_dfs, original_clusters.num_clusters, path=evolution_path)
    if new_metrics:
        metric_names, metric_values = zip(*[(k, v) for k, v in base_metrics.items()])
        
        metrics_evolution = []
        for i, metric_name in enumerate(metric_names):
            metrics_evolution.append((metric_values[i], [degraded_metric[metric_name] for degraded_metric in new_metrics]))

        plt.figure(figsize=(10, 6))
        for i, (metric_name, metric_values) in enumerate(metrics_evolution):
            plt.plot(range(len(metric_values)), metric_values, label=metric_name)
        plt.xlabel('Degraded DataFrame Index')
        plt.ylabel('Metric Value')
        plt.title('Evolution of Metrics Across Degraded DataFrames')
        plt.legend()
        plt.grid(True)
        plt.tight_layout(pad=2.0)

        if path:
            os.makedirs(path, exist_ok=True)
            plt.savefig(f"{path}/metrics_evolution.png")
            plt.close()
        else:
            plt.show()