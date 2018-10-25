# encoding=utf8

import nltk
import pickle
import re
import numpy as np

nltk.download('stopwords')
from nltk.corpus import stopwords

# Paths for all resources for the bot.
RESOURCE_PATH = {
    'INTENT_RECOGNIZER': './models/intent_recognizer.pkl',
    'TAG_CLASSIFIER': './models/tag_classifier.pkl',
    'TFIDF_VECTORIZER': './models/tfidf_vectorizer.pkl',
    'THREAD_EMBEDDINGS_FOLDER': 'thread_embeddings_by_tags',
    'WORD_EMBEDDINGS': './data/starspace_embeddings.tsv',
}


def text_prepare(text):
    """Performs tokenization and simple preprocessing."""
    
    replace_by_space_re = re.compile('[/(){}\[\]\|@,;]')
    bad_symbols_re = re.compile('[^0-9a-z #+_]')
    stopwords_set = set(stopwords.words('english'))

    text = text.lower()
    text = replace_by_space_re.sub(' ', text)
    text = bad_symbols_re.sub('', text)
    text = ' '.join([x for x in text.split() if x and x not in stopwords_set])

    return text.strip()


def load_embeddings(embeddings_path):
    """Loads pre-trained word embeddings from tsv file.

    Args:
      embeddings_path - path to the embeddings file.

    Returns:
      embeddings - dict mapping words to vectors;
      embeddings_dim - dimension of the vectors.
    """
    data = []
    for line in open(embeddings_path, encoding='utf-8'):
        data.append(line.strip().split('\t'))
    embeddings_dims = list(map(lambda x: len(x) - 1, data))
    embeddings_dim = max(set(embeddings_dims), key=lambda val: embeddings_dims.count(val))
    embeddings = {line[0]: np.array(line[1:]).astype(np.float32) for line in data if len(line) - 1 == embeddings_dim}
    
    return embeddings, embeddings[list(embeddings.keys())[-1]].shape[0]

def question_to_vec(question, embeddings, dim):
    """
        question: a string
        embeddings: dict where the key is a word and a value is its' embedding
        dim: size of the representation

        result: vector representation for the question
    """
    result = np.zeros(dim)
    n = 0
    for word in question.split(' '):
        if word in embeddings:
            result += embeddings[word]
            n += 1
            
    return result / max(1, n)

def pickle_object(obj, filename, protocol=4):
    """Pickles file to the file."""
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)

def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)
