"""
'ClassifierMetrics' dataclass is used to store the metrics of a classifier. along with the helper
function 'calculate_metrics' to calculate the metrics of a classifier given the true and predicted
values of the classifier.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


@dataclass
class ClassifierMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: np.ndarray


def get_metrics(
    y_true: np.ndarray | pd.Series, y_pred: np.ndarray | pd.Series
) -> ClassifierMetrics:
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    return ClassifierMetrics(accuracy, precision, recall, f1, cm)
