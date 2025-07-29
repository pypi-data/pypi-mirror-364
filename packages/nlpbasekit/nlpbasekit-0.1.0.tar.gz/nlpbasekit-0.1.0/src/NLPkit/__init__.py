"""
NLPkit
======

Scikit-learn–style text-classification wrappers with built-in
tokenisation, normalisation and vectorisation utilities.

Import the high-level classes directly:

    >>> from nlp_kit import Classifier, SupportVectorClassifier
"""

from importlib import metadata as _meta


from ._version import __version__


from .models.classifier import Classifier
from .models.classifier import SupportVectorClassifier
from .models.classifier import DTC
from .models.classifier import NeigbhorClassifier
from .models.classifier import SGD
from .models.classifier import GBC
from .models.classifier import GaussianProcess
from .models.classifier import NMeans

__all__ = [
    "Classifier",
    "SupportVectorClassifier",
    "DTC",
    "NeigbhorClassifier",
    "SGD",
    "GBC",
    "GaussianProcess",
    "NMeans",
    "__version__",
]
