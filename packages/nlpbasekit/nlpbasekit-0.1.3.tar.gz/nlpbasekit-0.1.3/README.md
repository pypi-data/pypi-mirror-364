# NLPkit

[![Azure Pipelines](https://dev.azure.com/scikit-learn/scikit-learn/_apis/build/status/scikit-learn.scikit-learn?branchName=main)](https://dev.azure.com/scikit-learn/scikit-learn/_build/latest?definitionId=1&branchName=main)
[![Codecov](https://codecov.io/gh/scikit-learn/scikit-learn/branch/main/graph/badge.svg?token=Pk8G9gg3y9)](https://codecov.io/gh/scikit-learn/scikit-learn)
[![CircleCI](https://circleci.com/gh/scikit-learn/scikit-learn/tree/main.svg?style=shield)](https://circleci.com/gh/scikit-learn/scikit-learn)
[![Nightly wheels](https://github.com/scikit-learn/scikit-learn/actions/workflows/wheels.yml/badge.svg?event=schedule)](https://github.com/scikit-learn/scikit-learn/actions?query=workflow%3A%22Wheel+builder%22+event%3Aschedule)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)]()
[![Pypi Version](https://img.shields.io/badge/pypi-0.1.2-blue)](https://pypi.org/project/nlpbasekit/)
[![DOI](https://zenodo.org/badge/21369/scikit-learn/scikit-learn.svg)](https://zenodo.org/badge/latestdoi/21369/scikit-learn/scikit-learn)
[![Benchmarked by ASV](https://img.shields.io/badge/Benchmarked%20by-asv-blue)](https://scikit-learn.org/scikit-learn-benchmarks)




A toolkit that wraps popular **scikit-learn** models with **NLP-aware** preprocessing and useful utilities. NLPkit simplifies text classification and clustering by offering:

- Tokenization
- Stop-word removal
- Contraction expansion
- Punctuation stripping
- Rare word filtering
- Vectorization
- Automated Model management & Evaluation



## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [LogisticClassifier API](#logisticclassifier-api)
   - [Initialization Parameters](#initialization-parameters)
   - [Model Methods](#model-methods)
5. [SupportVectorClassifier API](#supportvectorclassifier-api)
6. [DTC API](#dtc-api)
7. [NeigbhorClassifier API](#neigbhorclassifier-api)
8. [SGD API](#sgd-api)
9. [GBC API](#gbc-api)
10. [GaussianProcess API](#gaussianprocess-api)
11. [NMeans API](#nmeans-api)


---
<a name="installation"></a>
## Installation

Install via pip:

```bash
pip install nlpkit
```



---
<a name="quick-start"></a>
## Quick Start

```python
from nlpkit import LogisticClassifier

# Sample data
docs = [
    "The food was absolutely fantastic!",
    "I can't stand the traffic here.",
    "What a beautiful experience that was.",
    "This product broke after one use.",
    "Totally worth the price!",
    "I wouldn't recommend this to anyone.",
    "Had a great time with my friends.",
    "The customer service was disappointing.",
    "Everything about this place was perfect.",
    "It was a complete waste of money."
]

labels = [
    "positive","negative","positive","negative","positive",
    "negative","positive","negative","positive","negative"]
# Initialize and train the classifier
clf = LogisticClassifier(
    embedding='tfidf',       # 'count' or 'tfidf'
    n=1,                     # 1 = unigram
    stop='english',          # language for stop words
    punc=True,               # remove punctuation
    normalization_method='lemmatization',  # or 'stemming'
    rare_words=0.01          # drop words in bottom 1%
)
clf.fit(docs, labels)

# Predict and evaluate
print(clf.predict(["What a wonderful experience?"]))
print(clf.getClassificationReport())
```

---
<a name="features"></a>
## Features

- **Text Preprocessing**
  - Tokenization
  - Stop-word removal
  - Contraction expansion (e.g., "don't" → "do not")
  - Punctuation removal
  - Rare word filtering by proportion or count
  - Normalization: stemming or lemmatization
- **Vectorization**
  - Bag-of-words (`CountVectorizer`)
  - TF-IDF (`TfidfVectorizer`)
- **Model Management**
  - `fit`, `predict`, `predict_proba`, `score`
  - Export trained pipeline to file
  - Inspect coefficients and intercept
- **Evaluation**
  - Confusion matrix
  - Classification report
  - Precision, recall, and F1 scores

---
<a name="logisticclassifier-api"></a>
## LogisticClassifier API
<a name="initialization-parameters"></a>
### Initialization Parameters

| Parameter              | Type                 | Default      | Description                                                           |
|------------------------|----------------------|--------------|-----------------------------------------------------------------------|
| `penalty`              | `str`                | `'l2'`       | Regularization penalty (see `LogisticRegression`).                    |
| `dual`                 | `bool`               | `False`      | Dual or primal formulation.                                           |
| `tol`                  | `float`              | `1e-4`       | Tolerance for stopping criteria.                                      |
| `C`                    | `float`              | `1.0`        | Inverse of regularization strength.                                   |
| _All other sklearn.linear_model LogisticRegression args_ |                      |              | Supported (e.g., `solver`, `max_iter`).                               |
| **NLP-specific**       |                      |              |                                                                       |
| `embedding`            | `str`                | `'count'`    | `'count'` or `'tfidf'`.                                               |
| `n`                    | `int`                | `1`          | N-gram size (1 = unigram, 2 = bigram, etc.).                          |
| `stop`                 | `str`                | `'english'`  | Stop-word language for NLTK.                                          |
| `punc`                 | `bool`               | `True`       | Remove punctuation if `True`.                                         |
| `extraction`           | `bool`               | `True`       | Expand contractions if `True`.                                        |
| `rare_words`           | `float` or `int`     | `0`          | Proportion or count threshold to drop rare words.                     |
| `normalization_method` | `str` or `None`      | `None`       | `'stemming'`, `'lemmatization'`, or `None`.                           |

<a name="model-methods"></a>
### Model Methods

```python
fit(X: List[str], y: List[Any]) -> None
``` 
Train on raw text and labels.

```python
predict(X: List[str]) -> np.ndarray
``` 
Predict class labels.

```python
predict_proba(X: List[str]) -> np.ndarray
``` 
Return class probabilities.

```python
score(X: List[str], y: List[Any]) -> float
``` 
Mean accuracy on test data.

```python
export_model(path: str, model_name: str) -> None
``` 
Save pipeline as `<path>/<model_name>.pkl`.

```python
getCoefficients() -> np.ndarray
``` 
Return learned feature coefficients.

```python
getIntercept() -> np.ndarray
``` 
Return model intercept.

```python
getConfusionMatrix() -> np.ndarray
``` 
Compute confusion matrix on the last predictions.

```python
getClassificationReport() -> str
``` 
Detailed precision, recall, F1 by class.

```python
getPrecisionScore() -> float
``` 
Precision score (binary or macro-averaged).

---
<a name="supportvectorclassifier-api"></a>
## SupportVectorClassifier API

All parameters in the first section are forwarded directly to `sklearn.svm.SVC` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`

After fitting, you can call the following methods:

```python
predict(X: List[str]) -> np.ndarray
predict_proba(X: List[str]) -> np.ndarray
score(X: List[str], y: List[Any]) -> float
getCoefficients() -> np.ndarray
getIntercept() -> np.ndarray
getConfusionMatrix() -> np.ndarray
getClassificationReport() -> str
getPrecisionScore() -> float
export_model(path: str, model_name: str) -> None
```
---
<a name="dtc-api"></a>
## DTC API

All parameters in the first section are forwarded directly to `sklearn.tree DecisionTreeClassifier` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`

After fitting, you can call the following methods:

```python
predict(X: List[str]) -> np.ndarray
predict_proba(X: List[str]) -> np.ndarray
score(X: List[str], y: List[Any]) -> float
getCoefficients() -> np.ndarray
getIntercept() -> np.ndarray
getConfusionMatrix() -> np.ndarray
getClassificationReport() -> str
getPrecisionScore() -> float
export_model(path: str, model_name: str) -> None
```

---
<a name="neigbhorclassifier-api"></a>
## NeigbhorClassifier API

All parameters in the first section are forwarded directly to `sklearn.neighbors KNeighborsClassifier` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`

After fitting, you can call the following methods:

```python
predict(X: List[str]) -> np.ndarray
predict_proba(X: List[str]) -> np.ndarray
score(X: List[str], y: List[Any]) -> float
getCoefficients() -> np.ndarray
getIntercept() -> np.ndarray
getConfusionMatrix() -> np.ndarray
getClassificationReport() -> str
getPrecisionScore() -> float
export_model(path: str, model_name: str) -> None
```
---
<a name="sgd-api"></a>
## SGD API

All parameters in the first section are forwarded directly to `sklearn.linear_model SGDClassifier` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`

After fitting, you can call the following methods:

```python
predict(X: List[str]) -> np.ndarray
predict_proba(X: List[str]) -> np.ndarray
score(X: List[str], y: List[Any]) -> float
getCoefficients() -> np.ndarray
getIntercept() -> np.ndarray
getConfusionMatrix() -> np.ndarray
getClassificationReport() -> str
getPrecisionScore() -> float
export_model(path: str, model_name: str) -> None
```
---
<a name="gbc-api"></a>
## GBC API

All parameters in the first section are forwarded directly to `sklearn.ensemble GradientBoostingClassifier` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`

After fitting, you can call the following methods:

```python
predict(X: List[str]) -> np.ndarray
predict_proba(X: List[str]) -> np.ndarray
score(X: List[str], y: List[Any]) -> float
getCoefficients() -> np.ndarray
getIntercept() -> np.ndarray
getConfusionMatrix() -> np.ndarray
getClassificationReport() -> str
getPrecisionScore() -> float
export_model(path: str, model_name: str) -> None
```
---
<a name="gaussianprocess-api"></a>
## GaussianProcess API

All parameters in the first section are forwarded directly to `sklearn.gaussian_process GaussianProcessClassifier` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`

After fitting, you can call the following methods:

```python
predict(X: List[str]) -> np.ndarray
predict_proba(X: List[str]) -> np.ndarray
score(X: List[str], y: List[Any]) -> float
getCoefficients() -> np.ndarray
getIntercept() -> np.ndarray
getConfusionMatrix() -> np.ndarray
getClassificationReport() -> str
getPrecisionScore() -> float
export_model(path: str, model_name: str) -> None
```

---
<a name="nmeans-api"></a>
## NMeans API

All parameters in the first section are forwarded directly to `sklearn.cluster KMeans` and behave exactly as in scikit-learn’s documentation.

- **NLP-specific parameters** (same as in the LogisticClassifier API):
  - `embedding`
  - `n`
  - `stop`
  - `punc`
  - `extraction`
  - `rare_words`
  - `normalization_method`


### Model Methods


```python
fit(X: array-like) -> None
``` 
Preprocess texts and fit `KMeans` on the feature matrix.

```python
predict(X: array-like) -> np.ndarray
``` 
Preprocess and predict cluster assignments.

```python
export_model(path: str, model_name: str) -> None
``` 
Save the fitted KMeans model as a `.joblib` file at `<path>/<model_name>.joblib`.

```python
get_centroids() -> np.ndarray
``` 
Return cluster centroids.

```python
get_labels() -> np.ndarray
``` 
Return labels assigned to each sample.

```python
get_inertia() -> float
``` 
Return the final inertia (sum of squared distances to nearest centroid).

```python
get_n_iterations() -> int
``` 
Return the number of iterations run.

```python
get_n_features() -> int
``` 
Return the number of features seen during fit.

```python
get_groups() -> Dict[str, List[str]]
``` 
Return a dict mapping each cluster label to the list of original inputs assigned to that cluster.

---