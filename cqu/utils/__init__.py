"""This is a util module mainly for the 'BaseClassifier' class and some other utility

This module provides the 'BaseClassifier' class along with some utility for internal 
use in the cqu module
"""

PLOT_FOLDER_NAME = "cqu_plots"

from .classifier import BaseClassifier
from .metrics import ClassifierMetrics, get_metrics
