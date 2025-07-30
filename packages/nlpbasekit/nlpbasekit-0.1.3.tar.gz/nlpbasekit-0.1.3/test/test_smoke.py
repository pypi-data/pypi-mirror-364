from nlpkit import LogisticClassifier

def test_fit_predict_roundtrip():
    docs = ["a b c", "b c d", "c d e"]
    y = [0, 1, 0]
    clf = LogisticClassifier(max_iter=10)
    clf.fit(docs, y)
    preds = clf.predict(["d e f"])
    assert len(preds) == 1
