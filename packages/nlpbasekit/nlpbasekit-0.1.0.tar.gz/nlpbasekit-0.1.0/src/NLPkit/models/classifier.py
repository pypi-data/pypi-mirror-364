from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report,precision_score,recall_score,f1_score,roc_auc_score

import joblib
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from gensim.models import Word2Vec
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import contractions
import os


from sklearn.gaussian_process.kernels import RBF
from sklearn.gaussian_process.kernels import ConstantKernel
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process.kernels import RationalQuadratic
from sklearn.gaussian_process.kernels import ExpSineSquared
from sklearn.gaussian_process import GaussianProcessClassifier



class LogisticClassifier:
  def __init__(self,penalty='l2', *, dual=False, tol=0.0001, C=1.0,fit_intercept=True, intercept_scaling=1, class_weight=None,random_state=None, solver='lbfgs', max_iter=100, multi_class='auto', verbose=0,warm_start=False, n_jobs=None, l1_ratio=None,embeding='count',n=1,stop='english', punc=True, extraction=True,rare_words=0,normalization_method=None):
    self.penalty=penalty
    self.dual=dual
    self.tol=tol
    self.C=C
    self.fit_intercept=fit_intercept
    self.intercept_scaling=intercept_scaling
    self.class_weight=class_weight
    self.random_state=random_state
    self.solver=solver
    self.max_iter=max_iter
    self.multi_class=multi_class
    self.verbose=verbose
    self.warm_start=warm_start
    self.n_jobs=n_jobs
    self.l1_ratio=l1_ratio
    self.embeding=embeding
    self.n=n
    self.stop=stop
    self.punc=punc
    self.extraction=extraction
    self.rare_words=rare_words
    self.normalization_method=normalization_method
    
    ########### Self Variables #################
    self.is_count_done = False
    self.is_tfidf_done = False
    self.is_first_time = True

 
  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    stop_words = set(stopwords.words(self.stop))
    # only download the punctuation for the first time 
    if self.is_first_time:
      nltk.download('punkt') #comment out letter
    processed_dataset = []
    for document in x:
        words = word_tokenize(document)
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
          #  print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x,y):

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    # train the model
    self.clf=LogisticRegression(penalty=self.penalty, dual=self.dual, tol=self.tol, C=self.C,fit_intercept=self.fit_intercept, intercept_scaling=self.intercept_scaling, class_weight=self.class_weight,random_state=self.random_state, solver=self.solver, max_iter=self.max_iter, multi_class=self.multi_class, verbose=self.verbose,warm_start=self.warm_start, n_jobs=self.n_jobs, l1_ratio=self.l1_ratio,).fit(self.res,self.y)

    if self.is_first_time:
      # store the score
      self.predicted_labels = self.clf.predict(self.res)
      # track the actual y for the scores metrics
      self.actual_labels = self.y
      # stores the score 
      self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
      self.is_first_time = False

    print("Model was fitted")

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)
  
  def predict_proba(self):
    return self.clf.predict_proba(self.res)

  def score(self):
    return self.classifier_score

  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def getCoefficients(self):
    return self.clf.coef_
  
  def getIntercept(self):
    return self.clf.intercept_

  
  def getConfusionMatrix(self):
    try:
      return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating confusion matrix:\n",str(e))

  def getClassificationReport(self):
    try:
      return classification_report(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating Classification Report:\n",str(e))

  def getPrecisionScore(self):
    try:
      # handling the binary or multi classification problems
      # print(len(set(self.actual_labels)))
      if len(set(self.actual_labels)) > 2:
        # multiclassification problem
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
      
      return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
    except Exception as e:
      print("Error in getting precision score:\n",str(e))


##################### Support Vector Machine
class SupportVectorClassifier:
  def __init__(self,*, C=1.0, kernel='rbf', 
               degree=3, gamma='scale', coef0=0.0, shrinking=True,
               probability=False, tol=0.001, cache_size=200, class_weight=None, 
               verbose=False, max_iter=-1, decision_function_shape='ovr', 
               break_ties=False, random_state=None, embeding='count',n=1,stop='english', 
               punc=True, extraction=True,rare_words=0,normalization_method=None):
    
    self.C = C
    self.kernel = kernel
    self.degree = degree
    self.gamma = gamma
    self.coef0 = coef0
    self.shrinking = shrinking
    self.probability = probability
    self.tol = tol
    self.cache_size = cache_size
    self.class_weight = class_weight
    self.verbose = verbose
    self.max_iter = max_iter
    self.decision_function_shape = decision_function_shape
    self.break_ties = break_ties
    self.random_state = random_state
    
    self.embeding=embeding
    self.n=n
    self.stop=stop
    self.punc=punc
    self.extraction=extraction
    self.rare_words=rare_words
    self.normalization_method=normalization_method

     ########### Self Variables #################
    self.is_count_done = False
    self.is_tfidf_done = False
    self.is_first_time = True


  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    # download the stopwords for the first time only
    if self.is_first_time:
      print("Downloading Stopwords")
      nltk.download('stopwords')
      print("Stop words Downloaded")

      print("Downloading Punctuations")
      nltk.download('punkt') #comment out letter
      print('Punctuations downloaded')

    stop_words = set(stopwords.words(self.stop))
    processed_dataset = []
    for document in x:
        words = word_tokenize(document)
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
          #  print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x,y):

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    print("PREPROCESSED X:\n", self.res)
    print("PREPROCESSED Y:\n",self.y)
    # train the model
    # self.clf=LogisticRegression(penalty=self.penalty, dual=self.dual, tol=self.tol, C=self.C,fit_intercept=self.fit_intercept, intercept_scaling=self.intercept_scaling, class_weight=self.class_weight,random_state=self.random_state, solver=self.solver, max_iter=self.max_iter, multi_class=self.multi_class, verbose=self.verbose,warm_start=self.warm_start, n_jobs=self.n_jobs, l1_ratio=self.l1_ratio,).fit(self.res,self.y)
    # self.clf = self.fit(self.res,self.y)
    self.clf = SVC(C=self.C, kernel=self.kernel, degree=self.degree, gamma=self.gamma, 
                   coef0=self.coef0, shrinking=self.shrinking, probability=self.probability, 
                   tol=self.tol, cache_size=self.cache_size, class_weight=self.class_weight, 
                   verbose=self.verbose, max_iter=self.max_iter, 
                   decision_function_shape=self.decision_function_shape, 
                   break_ties=self.break_ties, random_state=self.random_state).fit(self.res,self.y)

    if self.is_first_time:
      # store the score
      self.predicted_labels = self.clf.predict(self.res)
      # track the actual y for the scores metrics
      self.actual_labels = self.y
      # stores the score 
      self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
      self.is_first_time = False

    print("Model was fitted")

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)
  
  def predict_proba(self):
    return self.clf.predict_proba(self.res)

  def score(self):
    return self.classifier_score

  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def getCoefficients(self):
    return self.clf.coef_
  
  def getIntercept(self):
    return self.clf.intercept_

  
  def getConfusionMatrix(self):
    try:
      return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating confusion matrix:\n",str(e))

  def getClassificationReport(self):
    try:
      return classification_report(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating Classification Report:\n",str(e))

  def getPrecisionScore(self):
    try:
      # handling the binary or multi classification problems
      # print(len(set(self.actual_labels)))
      if len(set(self.actual_labels)) > 2:
        # multiclassification problem
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
      
      return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
    except Exception as e:
      print("Error in getting precision score:\n",str(e))


####################### DECISION TREE CLASSIFIER ###################### 

class DTC:
  def __init__(self,*,criterion='gini', splitter='best', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None, random_state=None, max_leaf_nodes=None, min_impurity_decrease=0.0, class_weight=None, ccp_alpha=0.0, embeding='count',n=1,stop='english', 
  punc=True, extraction=True,rare_words=0,normalization_method=None):

    # Initialize instance variables directly
        self.criterion = criterion
        self.splitter = splitter
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.random_state = random_state
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.class_weight = class_weight
        self.ccp_alpha = ccp_alpha
        self.embeding = embeding
        self.n = n
        self.stop = stop
        self.punc = punc
        self.extraction = extraction
        self.rare_words = rare_words
        self.normalization_method = normalization_method

        ########### Self Variables #################
        self.is_count_done = False
        self.is_tfidf_done = False
        self.is_first_time = True




  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    # download the stopwords for the first time only
    if self.is_first_time:
      print("Downloading Stopwords")
      nltk.download('stopwords')
      print("Stop words Downloaded")

      print("Downloading Punctuations")
      nltk.download('punkt') #comment out letter
      print('Punctuations downloaded')

    stop_words = set(stopwords.words(self.stop))
    processed_dataset = []
    for document in x:
        words = word_tokenize(document)
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
          #  print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x,y):

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    print("PREPROCESSED X:\n", self.res)
    print("PREPROCESSED Y:\n",self.y)
    # train the model
    
    self.clf = DecisionTreeClassifier(criterion=self.criterion, splitter=self.splitter, 
            max_depth=self.max_depth, 
            min_samples_split=self.min_samples_split, 
            min_samples_leaf=self.min_samples_leaf, 
            min_weight_fraction_leaf=self.min_weight_fraction_leaf, 
            max_features=self.max_features, 
            random_state=self.random_state, 
            max_leaf_nodes=self.max_leaf_nodes, 
            min_impurity_decrease=self.min_impurity_decrease, 
            class_weight=self.class_weight, 
            ccp_alpha=self.ccp_alpha).fit(self.res,self.y)

    if self.is_first_time:
      # store the score
      self.predicted_labels = self.clf.predict(self.res)
      # track the actual y for the scores metrics
      self.actual_labels = self.y
      # stores the score 
      self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
      self.is_first_time = False

    print("Model was fitted")

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)
  
  def predict_proba(self):
    return self.clf.predict_proba(self.res)

  def score(self):
    return self.classifier_score

  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def getCoefficients(self):
    return self.clf.coef_
  
  def getIntercept(self):
    return self.clf.intercept_

  
  def getConfusionMatrix(self):
    try:
      return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating confusion matrix:\n",str(e))

  def getClassificationReport(self):
    try:
      return classification_report(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating Classification Report:\n",str(e))

  def getPrecisionScore(self):
    try:
      # handling the binary or multi classification problems
      # print(len(set(self.actual_labels)))
      if len(set(self.actual_labels)) > 2:
        # multiclassification problem
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
      
      return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
    except Exception as e:
      print("Error in getting precision score:\n",str(e))

###################### KNN #############################################
class NeigbhorClassifier:
  def __init__(self,n_neighbors=5, *, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', metric_params=None, n_jobs=None,embeding='count',n=1,stop='english', 
  punc=True, extraction=True,rare_words=0,normalization_method=None):

    # Initialize instance variables
    self.n_neighbors = n_neighbors
    self.weights = weights
    self.algorithm = algorithm
    self.leaf_size = leaf_size
    self.p = p
    self.metric = metric
    self.metric_params = metric_params
    self.n_jobs = n_jobs
    self.embeding = embeding
    self.n = n
    self.stop = stop
    self.punc = punc
    self.extraction = extraction
    self.rare_words = rare_words
    self.normalization_method = normalization_method

      ########### Self Variables #################
    self.is_count_done = False
    self.is_tfidf_done = False
    self.is_first_time = True




  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    # download the stopwords for the first time only
    if self.is_first_time:
      print("Downloading Stopwords")
      nltk.download('stopwords')
      print("Stop words Downloaded")

      print("Downloading Punctuations")
      nltk.download('punkt') #comment out letter
      print('Punctuations downloaded')

    stop_words = set(stopwords.words(self.stop))
    processed_dataset = []
    for document in x:
        words = word_tokenize(document)
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
          #  print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x,y):

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    print("PREPROCESSED X:\n", self.res)
    print("PREPROCESSED Y:\n",self.y)
    # train the model
    
    self.clf = KNeighborsClassifier( n_neighbors=self.n_neighbors, weights=self.weights, 
            algorithm=self.algorithm, leaf_size=self.leaf_size, p=self.p, 
            metric=self.metric, metric_params=self.metric_params, 
            n_jobs=self.n_jobs).fit(self.res,self.y)

    if self.is_first_time:
      # store the score
      self.predicted_labels = self.clf.predict(self.res)
      # track the actual y for the scores metrics
      self.actual_labels = self.y
      # stores the score 
      self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
      self.is_first_time = False

    print("Model was fitted")

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)
  
  def predict_proba(self):
    return self.clf.predict_proba(self.res)

  def score(self):
    return self.classifier_score

  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def getCoefficients(self):
    return self.clf.coef_
  
  def getIntercept(self):
    return self.clf.intercept_

  
  def getConfusionMatrix(self):
    try:
      return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating confusion matrix:\n",str(e))

  def getClassificationReport(self):
    try:
      return classification_report(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating Classification Report:\n",str(e))

  def getPrecisionScore(self):
    try:
      # handling the binary or multi classification problems
      # print(len(set(self.actual_labels)))
      if len(set(self.actual_labels)) > 2:
        # multiclassification problem
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
      
      return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
    except Exception as e:
      print("Error in getting precision score:\n",str(e))


########################### Stochastic Gradient Descent ##############

from sklearn.linear_model import SGDClassifier
class SGD:
  def __init__(self,loss='hinge', *, 
               penalty='l2', alpha=0.0001, l1_ratio=0.15, 
               fit_intercept=True, max_iter=1000, tol=0.001, 
               shuffle=True, verbose=0, epsilon=0.1, n_jobs=None, 
               random_state=None, learning_rate='optimal', eta0=0.0, 
               power_t=0.5, early_stopping=False, validation_fraction=0.1, 
               n_iter_no_change=5, class_weight=None, warm_start=False, 
               average=False, embeding='count',n=1,stop='english', 
               punc=True, extraction=True,rare_words=0,normalization_method=None):
    
        # Initialize instance variables
        self.loss = loss
        self.penalty = penalty
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.fit_intercept = fit_intercept
        self.max_iter = max_iter
        self.tol = tol
        self.shuffle = shuffle
        self.verbose = verbose
        self.epsilon = epsilon
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.learning_rate = learning_rate
        self.eta0 = eta0
        self.power_t = power_t
        self.early_stopping = early_stopping
        self.validation_fraction = validation_fraction
        self.n_iter_no_change = n_iter_no_change
        self.class_weight = class_weight
        self.warm_start = warm_start
        self.average = average
        self.embeding = embeding
        self.n = n
        self.stop = stop
        self.punc = punc
        self.extraction = extraction
        self.rare_words = rare_words
        self.normalization_method = normalization_method

        ########### Self Variables #################
        self.is_count_done = False
        self.is_tfidf_done = False
        self.is_first_time = True



  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    nltk.download('stopwords')
    stop_words = set(stopwords.words(self.stop))
    nltk.download('punkt') #comment out letter
    processed_dataset = []
    for document in x:
        words = word_tokenize(document)
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
          #  print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x,y):

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    print("PREPROCESSED X:\n", self.res)
    print("PREPROCESSED Y:\n",self.y)
    # train the model
    
    self.clf =SGDClassifier(
            loss=self.loss, penalty=self.penalty, alpha=self.alpha, 
            l1_ratio=self.l1_ratio, fit_intercept=self.fit_intercept, 
            max_iter=self.max_iter, tol=self.tol, shuffle=self.shuffle, 
            verbose=self.verbose, epsilon=self.epsilon, n_jobs=self.n_jobs, 
            random_state=self.random_state, learning_rate=self.learning_rate, 
            eta0=self.eta0, power_t=self.power_t, early_stopping=self.early_stopping, 
            validation_fraction=self.validation_fraction, 
            n_iter_no_change=self.n_iter_no_change, class_weight=self.class_weight, 
            warm_start=self.warm_start, average=self.average
        ).fit(self.res,self.y)

    if self.is_first_time:
      # store the score
      self.predicted_labels = self.clf.predict(self.res)
      # track the actual y for the scores metrics
      self.actual_labels = self.y
      # stores the score 
      self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
      self.is_first_time = False

    print("Model was fitted")


  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)
  
  def predict_proba(self):
    return self.clf.predict_proba(self.res)

  def score(self):
    return self.classifier_score

  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def getCoefficients(self):
    return self.clf.coef_
  
  def getIntercept(self):
    return self.clf.intercept_

  
  def getConfusionMatrix(self):
    try:
      return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating confusion matrix:\n",str(e))

  def getClassificationReport(self):
    try:
      return classification_report(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating Classification Report:\n",str(e))

  def getPrecisionScore(self):
    try:
      # handling the binary or multi classification problems
      # print(len(set(self.actual_labels)))
      if len(set(self.actual_labels)) > 2:
        # multiclassification problem
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
      
      return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
    except Exception as e:
      print("Error in getting precision score:\n",str(e))


################### Gradient Boosting Classifier ############

from sklearn.ensemble import GradientBoostingClassifier

class GBC:
  def __init__(self,*, loss='log_loss', learning_rate=0.1, 
               n_estimators=100, subsample=1.0, criterion='friedman_mse', 
               min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, 
               max_depth=3, min_impurity_decrease=0.0, init=None, random_state=None, 
               max_features=None, verbose=0, max_leaf_nodes=None, warm_start=False, 
               validation_fraction=0.1, n_iter_no_change=None, tol=0.0001, ccp_alpha=0.0,
               embeding='count',n=1,stop='english', 
               punc=True, extraction=True,rare_words=0,normalization_method=None):
    
        # Initialize instance variables
        self.loss = loss
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.subsample = subsample
        self.criterion = criterion
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_depth = max_depth
        self.min_impurity_decrease = min_impurity_decrease
        self.init = init
        self.random_state = random_state
        self.max_features = max_features
        self.verbose = verbose
        self.max_leaf_nodes = max_leaf_nodes
        self.warm_start = warm_start
        self.validation_fraction = validation_fraction
        self.n_iter_no_change = n_iter_no_change
        self.tol = tol
        self.ccp_alpha = ccp_alpha
        self.embeding = embeding
        self.n = n
        self.stop = stop
        self.punc = punc
        self.extraction = extraction
        self.rare_words = rare_words
        self.normalization_method = normalization_method

        ########### Self Variables #################
        self.is_count_done = False
        self.is_tfidf_done = False
        self.is_first_time = True



  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    nltk.download('stopwords')
    stop_words = set(stopwords.words(self.stop))
    nltk.download('punkt') #comment out letter
    processed_dataset = []
    for document in x:
        words = word_tokenize(document)
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
          #  print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x,y):

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    print("PREPROCESSED X:\n", self.res)
    print("PREPROCESSED Y:\n",self.y)
    # train the model
    self.clf =GradientBoostingClassifier(
            loss=self.loss, learning_rate=self.learning_rate, 
            n_estimators=self.n_estimators, subsample=self.subsample, 
            criterion=self.criterion, min_samples_split=self.min_samples_split, 
            min_samples_leaf=self.min_samples_leaf, 
            min_weight_fraction_leaf=self.min_weight_fraction_leaf, 
            max_depth=self.max_depth, 
            min_impurity_decrease=self.min_impurity_decrease, 
            init=self.init, random_state=self.random_state, 
            max_features=self.max_features, verbose=self.verbose, 
            max_leaf_nodes=self.max_leaf_nodes, warm_start=self.warm_start, 
            validation_fraction=self.validation_fraction, 
            n_iter_no_change=self.n_iter_no_change, tol=self.tol, 
            ccp_alpha=self.ccp_alpha
        ).fit(self.res,self.y)

    if self.is_first_time:
      # store the score
      self.predicted_labels = self.clf.predict(self.res)
      # track the actual y for the scores metrics
      self.actual_labels = self.y
      # stores the score 
      self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
      self.is_first_time = False

    print("Model was fitted")

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)
  
    # returns the predictions
    return self.clf.predict(self.res)

  
  def predict_proba(self):
    return self.clf.predict_proba(self.res)

  def score(self):
    return self.classifier_score

  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def getCoefficients(self):
    return self.clf.coef_
  
  def getIntercept(self):
    return self.clf.intercept_

  
  def getConfusionMatrix(self):
    try:
      return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating confusion matrix:\n",str(e))

  def getClassificationReport(self):
    try:
      return classification_report(self.actual_labels.tolist(),self.predicted_labels)
    except Exception as e:
      print("Error during generating Classification Report:\n",str(e))

  def getPrecisionScore(self):
    try:
      # handling the binary or multi classification problems
      # print(len(set(self.actual_labels)))
      if len(set(self.actual_labels)) > 2:
        # multiclassification problem
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
      
      return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
    except Exception as e:
      print("Error in getting precision score:\n",str(e))


#################### Guassian Process ##########################

class GaussianProcess():
    def __init__(self,kernel=None, *, optimizer='fmin_l_bfgs_b', n_restarts_optimizer=0, max_iter_predict=100, warm_start=False, copy_X_train=True, random_state=None, multi_class='one_vs_rest', n_jobs=None,embeding='count',n=1,stop='english',punc=True, extraction=True,rare_words=0,normalization_method=None):

        self.kernel=kernel
        self.optimizer=optimizer
        self.n_restarts_optimizer=n_restarts_optimizer
        self.max_iter_predict=max_iter_predict
        self.warm_start=warm_start
        self.copy_X_train=copy_X_train
        self.random_state=random_state
        self.multi_class=multi_class
        self.n_jobs=n_jobs

        
        self.embeding = embeding
        self.n = n
        self.stop = stop
        self.punc = punc
        self.extraction = extraction
        self.rare_words = rare_words
        self.normalization_method = normalization_method

        ########### Self Variables #################
        self.is_count_done = False
        self.is_tfidf_done = False
        self.is_first_time = True

    def krbf(self,a,b):
        self.kernel = a * RBF(b)

    def kMatern(self,a,b,c):
        self.kernel = a * Matern(length_scale=b, nu=c)

    def kRationalQuadratic(self,a,b,c):
        self.kernel = a * RationalQuadratic(length_scale=b, alpha=c)

    def kExpSineSquared(self,a,b,c):
        self.kernel = a * ExpSineSquared(length_scale=b, periodicity=c)
    def kConstantKernel(self,a,b,c,d):
        self.kernel = ConstantKernel(a, constant_value_bounds=(b, c)) * RBF(d)

    def stemming(self,x):
      nltk.download('punkt')  # this must be commented letter
      punkt_path = nltk.data.find('tokenizers/punkt')
      # print("Punctuation Downloaded", punkt_path)

      stemmed_documtn=[]
      for text in x:
        words = word_tokenize(text)
        porter = PorterStemmer()
        stemmed_words = [porter.stem(word) for word in words]
        stemmed_text = ' '.join(stemmed_words)
        stemmed_documtn.append(stemmed_text)
      #print(stemmed_documtn)
      return stemmed_documtn

    def lemitization(self,x):
      lemmatizer = WordNetLemmatizer()
      lemmitize_sentences=[]
      for sentence in x:
        words = word_tokenize(sentence)
        lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
        lemmatized_sentence = ' '.join(lemmatized_words)
        lemmitize_sentences.append(lemmatized_sentence)
      #print("Lemmatized sentence:", lemmitize_sentences)
      # print("Lemmetization done")
      return lemmitize_sentences

    def stop_words(self,x):
      nltk.download('stopwords')
      stop_words = set(stopwords.words(self.stop))
      nltk.download('punkt') #comment out letter
      processed_dataset = []
      for document in x:
          words = word_tokenize(document)
          filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
          processed_dataset.append(' '.join(filtered_words))
      #print("stop  words removed : ", processed_dataset)
      # print("Stop words done")
      return processed_dataset

    def extraction_func(self,x):
      expanded_contract = []
      for i in x:
        expanded_text = contractions.fix(i)
        expanded_contract.append(expanded_text)
      #print("Expanded Contract:\n", expanded_contract)
      # print("Extraction done")
      return expanded_contract
    
    def remove(self,x):
      def remove_punctuation(sentence):
          translator = str.maketrans("", "", string.punctuation)
          sentence_without_punct = sentence.translate(translator)
          return sentence_without_punct
      def remove_special_characters(sentence):
        cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
        return cleaned_sentence
      sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
      sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
      #print(sentences_without_special_chars)
      # print("Punctuation done")
      return sentences_without_special_chars

    def rare_word_removal(self,phrase_list,y):
      word_list = [word for phrase in phrase_list for word in phrase.split()]
      word_counts = Counter(word_list)
      tcount=0
      tcount_lst=[]
      elementlst=[]
      for word,count in word_counts.items():
        tcount=count+tcount
        tcount_lst.append(count)
        elementlst.append(word)
      percent=list(np.array(tcount_lst)/tcount)
      words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
      cleaned_data=[]
      for i in phrase_list:
          i=i.split()
          ele=[word for word in i if not word in words]
          ele=' '.join(ele)
          cleaned_data.append(ele)
      dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
      dataframe.drop_duplicates(inplace=True)
      dataframe.dropna(inplace=True)
      # print("Rare words done")
      return dataframe

    def countvectorizer(self,x):
      if self.is_count_done:
        X = self.vectorizer.transform(x)
        # print("Testing Shape:\t",X.shape)
      else:
        self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
        X = self.vectorizer.fit_transform(x)
        # print("Training shape:\t",X.shape)
        self.is_count_done = True

      # print("CountVectorizer")
      return X

    def tfidf(self,x):
      if self.is_tfidf_done:
        tfidf_matrix = self.tfidf_vectorizer.transform(x)
        # print("Testing Shape:\t",tfidf_matrix)

      else:
        self.tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
        # print("Training Shape:\t",tfidf_matrix.shape)
        self.is_tfidf_done = True

      # print("TFIDF")
      return tfidf_matrix
    
    
    def preprocessing(self,x,y):
      self.res=x
      self.y = y

      try:
        if self.normalization_method=="L":
            #  print("lemitization")
            self.res=self.lemitization(self.res)
        elif self.normalization_method =="S":
            #  print("stemming")
            self.res=self.stemming(self.res)
        elif self.normalization_method ==None:
            raise ValueError("No Normalization is Applied!")
        else:
            raise ValueError("Invalid normalization method!")

      except Exception as e:
        print(str(e))

      try:
        if self.stop:
            # print("remove stop words")
            self.res=self.stop_words(self.res)
      except Exception as e:
            print("Error Occured in Removing Stopwords:\n",str(e))

      try:
        if self.extraction==True:
            #  print("extraction ture")
            self.res=self.extraction_func(self.res)
      except Exception as e:
        print("Error Occured in Contraction:\n",str(e))

      try:
        if self.punc==True:
                # print("punctuation true")
                self.res=self.remove(self.res)
      except Exception as e:
        print("Error Occured in Punctuation Removal:\n",str(e))

      try:
        if  self.rare_words > 0:
            #  print("remove rare words : ", self.rare_words)
            self.res=self.rare_word_removal(self.res,self.y)
            x=self.res.iloc[:,0].tolist()
            self.y=self.res.iloc[:,1].tolist()
            self.res=x
      except Exception as e:
        print("Error Occured in Removing Rare Words:\n",str(e))

      try:
        if self.embeding=="count":
            #  print("count")
            self.res=self.countvectorizer(self.res)

        elif self.embeding=="tfidf":
            #  print("tfidf")
            self.res=self.tfidf(self.res)
      
        # Word2Vec Logic Here ... 
        else:
          print("error message embedding!!!!")

      except Exception as e:
        print("Error Occured in Embedding:\n",str(e))

    def fit(self,x,y):

      # do preprocessing
      self.preprocessing(x,y)

      print("Model is being trained")
      print("PREPROCESSED X:\n", self.res)
      print("PREPROCESSED Y:\n",self.y)
      # train the model
    
        # Create a GaussianProcessClassifier instance with all instance variables
      self.clf = GaussianProcessClassifier(
            kernel=self.kernel, optimizer=self.optimizer, 
            n_restarts_optimizer=self.n_restarts_optimizer, 
            max_iter_predict=self.max_iter_predict, 
            warm_start=self.warm_start, copy_X_train=self.copy_X_train, 
            random_state=self.random_state, multi_class=self.multi_class, 
            n_jobs=self.n_jobs
        ).fit(self.res.toarray(),self.y)

      if self.is_first_time:
        # store the score
        self.predicted_labels = self.clf.predict(self.res.toarray())
        # track the actual y for the scores metrics
        self.actual_labels = self.y
        # stores the score 
        self.classifier_score = accuracy_score(self.actual_labels,self.predicted_labels)
        self.is_first_time = False

      print("Model was fitted")

    def predict(self,x):
      # print("In Predict")
      x_len = len(x)
      arr = np.zeros((x_len,))

      self.preprocessing(x,arr)
    
      # returns the predictions
      return self.clf.predict(self.res.toarray())

    
    def predict_proba(self):
      return self.clf.predict_proba(self.res)

    def score(self):
      return self.classifier_score

    def export_model(self,path='', model_name=''):
      try:
        if path and model_name:
            # save the model
            if not os.path.exists(path):
                  os.makedirs(path)

              # Save the model
            with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                  joblib.dump(self.clf, file)
                  print(f"Your model has been saved to {os.path.join(path, model_name)}")

      except Exception as e:
          print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

    def getCoefficients(self):
      return self.clf.coef_
    
    def getIntercept(self):
      return self.clf.intercept_

    
    def getConfusionMatrix(self):
      try:
        return confusion_matrix(self.actual_labels.tolist(),self.predicted_labels)
      except Exception as e:
        print("Error during generating confusion matrix:\n",str(e))

    def getClassificationReport(self):
      try:
        return classification_report(self.actual_labels.tolist(),self.predicted_labels)
      except Exception as e:
        print("Error during generating Classification Report:\n",str(e))

    def getPrecisionScore(self):
      try:
        # handling the binary or multi classification problems
        # print(len(set(self.actual_labels)))
        if len(set(self.actual_labels)) > 2:
          # multiclassification problem
          return precision_score(self.actual_labels.tolist(),self.predicted_labels,average='weighted')  
        
        return precision_score(self.actual_labels.tolist(),self.predicted_labels,)
      except Exception as e:
        print("Error in getting precision score:\n",str(e))


from sklearn.cluster import KMeans
# KMeans
class NMeans():
  def __init__(self,n_clusters=8, *, init='k-means++', n_init='warn', max_iter=300, tol=0.0001, verbose=0, random_state=None, copy_x=True, algorithm='lloyd',  embeding='count',n=1,stop='english', 
  punc=True, extraction=True,rare_words=0,normalization_method=None):
        self.n_clusters=n_clusters
        self.init=init
        self.n_init=n_init
        self.max_iter=max_iter
        self.tol=tol
        self.verbose=verbose
        self.random_state=random_state
        self.copy_x=copy_x
        self.algorithm=algorithm
    
        self.embeding = embeding
        self.n = n
        self.stop = stop
        self.punc = punc
        self.extraction = extraction
        self.rare_words = rare_words
        self.normalization_method = normalization_method

        ########### Self Variables #################
        self.is_count_done = False
        self.is_tfidf_done = False
        self.is_first_time = True

  def stemming(self,x):
    nltk.download('punkt')  # this must be commented letter
    punkt_path = nltk.data.find('tokenizers/punkt')
    # print("Punctuation Downloaded", punkt_path)

    stemmed_documtn=[]
    for text in x:
      words = word_tokenize(text)
      porter = PorterStemmer()
      stemmed_words = [porter.stem(word) for word in words]
      stemmed_text = ' '.join(stemmed_words)
      stemmed_documtn.append(stemmed_text)
    #print(stemmed_documtn)
    return stemmed_documtn

  def lemitization(self,x):
    lemmatizer = WordNetLemmatizer()
    lemmitize_sentences=[]
    for sentence in x:
      words = word_tokenize(sentence)
      lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
      lemmatized_sentence = ' '.join(lemmatized_words)
      lemmitize_sentences.append(lemmatized_sentence)
    #print("Lemmatized sentence:", lemmitize_sentences)
    # print("Lemmetization done")
    return lemmitize_sentences

  def stop_words(self,x):
    nltk.download('stopwords')
    stop_words = set(stopwords.words(self.stop))
    nltk.download('punkt') #comment out letter
    processed_dataset = []
    print("c1")
    for document in x:
        words = word_tokenize(document)
        try:
          filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        except Exception as e:
          print("c5",str(e))
        processed_dataset.append(' '.join(filtered_words))
    #print("stop  words removed : ", processed_dataset)
    # print("Stop words done")
    return processed_dataset

  def extraction_func(self,x):
    expanded_contract = []
    for i in x:
      expanded_text = contractions.fix(i)
      expanded_contract.append(expanded_text)
    #print("Expanded Contract:\n", expanded_contract)
    # print("Extraction done")
    return expanded_contract
  
  def remove(self,x):
    def remove_punctuation(sentence):
        translator = str.maketrans("", "", string.punctuation)
        sentence_without_punct = sentence.translate(translator)
        return sentence_without_punct
    def remove_special_characters(sentence):
      cleaned_sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
      return cleaned_sentence
    sentences_without_punct = [remove_punctuation(sentence) for sentence in x]
    sentences_without_special_chars = [remove_special_characters(sentence) for sentence in sentences_without_punct]
    #print(sentences_without_special_chars)
    # print("Punctuation done")
    return sentences_without_special_chars

  def rare_word_removal(self,phrase_list,y):
    word_list = [word for phrase in phrase_list for word in phrase.split()]
    word_counts = Counter(word_list)
    tcount=0
    tcount_lst=[]
    elementlst=[]
    for word,count in word_counts.items():
      tcount=count+tcount
      tcount_lst.append(count)
      elementlst.append(word)
    percent=list(np.array(tcount_lst)/tcount)
    words=[elementlst[i] for i,j in enumerate(percent) if j<=self.rare_words]
    cleaned_data=[]
    for i in phrase_list:
        i=i.split()
        ele=[word for word in i if not word in words]
        ele=' '.join(ele)
        cleaned_data.append(ele)
    dataframe=pd.DataFrame({'text':cleaned_data, 'label':y})
    dataframe.drop_duplicates(inplace=True)
    dataframe.dropna(inplace=True)
    # print("Rare words done")
    return dataframe

  def countvectorizer(self,x):
    if self.is_count_done:
      X = self.vectorizer.transform(x)
      # print("Testing Shape:\t",X.shape)
    else:
      self.vectorizer = CountVectorizer(ngram_range=(self.n, self.n))
      X = self.vectorizer.fit_transform(x)
      # print("Training shape:\t",X.shape)
      self.is_count_done = True

    # print("CountVectorizer")
    return X

  def tfidf(self,x):
    if self.is_tfidf_done:
      tfidf_matrix = self.tfidf_vectorizer.transform(x)
      # print("Testing Shape:\t",tfidf_matrix)

    else:
      self.tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = self.tfidf_vectorizer.fit_transform(x)
      # print("Training Shape:\t",tfidf_matrix.shape)
      self.is_tfidf_done = True

    # print("TFIDF")
    return tfidf_matrix
  
  
  def preprocessing(self,x,y):
    self.res=x
    self.y = y

    try:
      if self.normalization_method=="L":
          #  print("lemitization")
          self.res=self.lemitization(self.res)
      elif self.normalization_method =="S":
          #  print("stemming")
          self.res=self.stemming(self.res)
      elif self.normalization_method ==None:
          raise ValueError("No Normalization is Applied!")
      else:
          raise ValueError("Invalid normalization method!")

    except Exception as e:
      print(str(e))

    try:
      if self.stop:
          # print("remove stop words")
          self.res=self.stop_words(self.res)
    except Exception as e:
          print("Error Occured in Removing Stopwords:\n",str(e))

    try:
      if self.extraction==True:
          #  print("extraction ture")
          self.res=self.extraction_func(self.res)
    except Exception as e:
       print("Error Occured in Contraction:\n",str(e))

    try:
      if self.punc==True:
              # print("punctuation true")
              self.res=self.remove(self.res)
    except Exception as e:
       print("Error Occured in Punctuation Removal:\n",str(e))

    try:
      if  self.rare_words > 0:
          #  print("remove rare words : ", self.rare_words)
          self.res=self.rare_word_removal(self.res,self.y)
          x=self.res.iloc[:,0].tolist()
          self.y=self.res.iloc[:,1].tolist()
          self.res=x
    except Exception as e:
       print("Error Occured in Removing Rare Words:\n",str(e))

    try:
      if self.embeding=="count":
          #  print("count")
           self.res=self.countvectorizer(self.res)

      elif self.embeding=="tfidf":
           print("tfidf")
           self.res=self.tfidf(self.res)
    
      # Word2Vec Logic Here ... 
      else:
        print("error message embedding!!!!")

    except Exception as e:
       print("Error Occured in Embedding:\n",str(e))

  def fit(self,x):

    self.X = x
    y = np.zeros(x.shape[0])

    # do preprocessing
    self.preprocessing(x,y)

    print("Model is being trained")
    print("PREPROCESSED X:\n", self.res)
    print("PREPROCESSED Y:\n",self.y)
    # train the model
    self.clf = KMeans(n_clusters=self.n_clusters, init=self.init,n_init=self.n_init, max_iter=self.max_iter, tol=self.tol, verbose=self.verbose, random_state=self.random_state, copy_x=self.copy_x, algorithm=self.algorithm)
    self.clf.fit(self.res)

    print("Model was fitted")

  def predict(self,x):
    # print("In Predict")
    x_len = len(x)
    arr = np.zeros((x_len,))

    self.preprocessing(x,arr)

    self.predictions = self.clf.predict(self.res)
    # returns the predictions
    return self.predictions


  def export_model(self,path='', model_name=''):
    try:
      if path and model_name:
          # save the model
          if not os.path.exists(path):
                os.makedirs(path)

             # Save the model
          with open(os.path.join(path, model_name + '.joblib'), 'wb') as file:
                joblib.dump(self.clf, file)
                print(f"Your model has been saved to {os.path.join(path, model_name)}")

    except Exception as e:
        print("Error Occured during exporting the model:\nThis may be due to invalid path. Try to enter valid path:\n", str(e))        

  def get_centroids(self):
    return self.clf.cluster_centers_
      
  def get_labels(self):
    return self.clf.labels_

  def get_inertia(self):
    return self.clf.inertia_

  def get_n_iterations(self):
    return self.clf.n_iter_

  def get_n_features(self):
    return self.clf.n_features_in_

  def get_groups(self):
        results=self.predictions
        u_results=np.unique(results)
        di={}
        for i in range(len(u_results)):
            di[f'grp_{u_results[i]}']=[]
        for i in range(len(results)):
            for j in range(len(u_results)):
                if results[i]==u_results[j]:
                    di[f'grp_{u_results[j]}'].append(self.X[i])
        
        return di
  

