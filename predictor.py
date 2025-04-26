import string
import nltk
import numpy as np
import random
from nltk.corpus import stopwords, wordnet
from nltk.stem.snowball import SnowballStemmer
from sentence_transformers import SentenceTransformer
from joblib import load  # For loading the saved model
import mysql.connector  # (Optional) if you need database connectivity
import warnings
warnings.filterwarnings("ignore")



nltk_data_dir = "./nltk_data"
nltk.data.path.append(nltk_data_dir)


ensemble = None
st_model = None
english_stopwords = None
stemmer = None


class Predictor():
    def __init__(self):
        self.ensemble = None
        self.st_model = None
        self.english_stopwords = None
        self.stemmer = None

    def ensure_nltk_resources(self):
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            try:
                nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)
            except Exception as e:
                return False


        try:
            nltk.data.find("corpora/wordnet")
        except LookupError:
            try:
                nltk.download('wordnet', download_dir=nltk_data_dir, quiet=True)
            except Exception as e:
                return False
        return True

    def load_models(self):
        try:
            self.english_stopwords = set(stopwords.words('english'))
            self.stemmer = SnowballStemmer('english')
            self.ensemble = load('voting_classifier_ensemble.joblib')
            self.st_model = SentenceTransformer('all-mpnet-base-v2')
            if self.english_stopwords == None or self.stemmer == None or self.ensemble == None or self.st_model == None:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def clean_text(self, text):
        if text is None or not isinstance(text, str) or text.strip() == '':
            return ''
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = text.split()
        tokens = [word for word in tokens if word not in self.english_stopwords]
        tokens = [self.stemmer.stem(word) for word in tokens]
        tokens = [word for word in tokens if word.isalpha() and len(word) > 1]
        return " ".join(tokens)

    def predict_category(self, text):
        cleaned = self.clean_text(text)
        embedding = self.st_model.encode([cleaned])
        embedding = np.array(embedding)
        prediction = self.ensemble.predict(embedding)
        return prediction[0]
