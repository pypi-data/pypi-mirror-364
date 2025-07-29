# NLPkit

A tiny toolkit that wraps several **scikit-learn** models with
*NLP-aware* preprocessing:

* Tokenisation (NLTK)
* Stop-word removal
* Stemming / lemmatisation
* Contraction expansion
* Auto Count or TF-IDF vectorisation

```python
from nlpkit import Classifier

docs = ["I love NLP", "NLP is awesome"]
labels = [1, 1]

clf = Classifier(embeding="tfidf", normalization_method="L")
clf.fit(docs, labels)

print(clf.predict(["NLP rocks"]))
