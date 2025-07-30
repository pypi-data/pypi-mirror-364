import json

import numpy as np
from sklearn.tree import DecisionTreeClassifier, _tree


def export_tree_as_hierarchy(tree, feature_names, X, y, hist_bins=10):
    tree_ = tree.tree_

    def recurse(node, indices, split=None):
        # If the node is not a leaf, compute the histogram for the split feature.
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            feat_idx = tree_.feature[node]
            threshold = tree_.threshold[node]
            
            classes_histograms = []
            target_values = y[indices]
            feature_values = X[indices, feat_idx]
            for target_value in np.unique(target_values):
                if isinstance(target_value, np.int64):
                    target_value = int(target_value)
                target_value_indices = np.where(target_values==target_value)[0]
                class_feature_values = feature_values[target_value_indices]
                hist, bin_edges = np.histogram(class_feature_values, bins=hist_bins)
                classes_histograms.append(
                    {
                        'class': target_value,
                        'counts': hist.tolist(),
                        'bin_edges': bin_edges.tolist()
                    }
                )
            
            left_indices = indices[feature_values <= threshold]
            right_indices = indices[feature_values > threshold]
            
            feature_name = feature_names[feat_idx]
            return {
                "id": node,
                "name": f"{feature_names[feat_idx]} <= {threshold:.2f}",
                "feature": feature_name,
                'split': split,
                "threshold": float(threshold),
                'classes_histograms': classes_histograms,
                "children": [
                    recurse(tree_.children_left[node], left_indices, split=f'{feature_name} < {threshold}'),
                    recurse(tree_.children_right[node], right_indices, split=f'{feature_name} >= {threshold}')
                ],
            }
        else:
            target_values = y[indices]
            unique_targets, counts = np.unique(target_values, return_counts=True)
            return {
                "id": node,
                "name": f"Leaf: {tree_.value[node].tolist()}",
                "value": tree_.value[node].tolist(),
                'target_distribution': {
                    'unique_targets': unique_targets,
                    'count': counts
                },
                'split': split,
                "samples": tree_.n_node_samples[node],
            }

    return recurse(0, np.arange(X.shape[0]))


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)
    

def fit(train_df, target, max_depth):
    tree = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    tree.fit(train_df, target)

    hierarchy = export_tree_as_hierarchy(
        tree=tree, 
        feature_names=train_df.columns, 
        X=train_df.values, 
        y=target.values
    )
    
    return json.dumps(
        obj={
            'tree': hierarchy,
            'metadata': {'max_depth': 3},
            'class_colors': [
                {
                    'class': 0,
                    'color': 'green'
                },
                {
                    'class': 1,
                    'color': 'red'
                }
            ]
        },
        cls=NumpyEncoder
    ) 
