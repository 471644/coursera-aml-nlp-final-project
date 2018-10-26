# encoding=utf8

import pickle
import re
import numpy as np
import scipy
import shelve

# Paths for all resources for the bot.
RESOURCE_PATH = {
    'INTENT_RECOGNIZER': './models/intent_recognizer.pkl',
    'TAG_CLASSIFIER': './models/tag_classifier.pkl',
    'HASHING_VECTORIZER': './models/hashing_vectorizer.pkl',
    'THREAD_EMBEDDINGS_FOLDER': 'thread_embeddings_by_tags',
    'WORD_EMBEDDINGS': './data/starspace_embeddings.shelve',
    'STOP_WORDS': './data/stopwords.pkl'
}


def text_prepare(text, stopwords_set):
    """Performs tokenization and simple preprocessing."""
    
    replace_by_space_re = re.compile('[/(){}\[\]\|@,;]')
    bad_symbols_re = re.compile('[^0-9a-z #+_]')

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
    embeddings = shelve.open(embeddings_path, 'r')
    embeddings_dim = embeddings[list(embeddings.keys())[0]].shape[0]
    
    return embeddings, embeddings_dim

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
    
def cos_cdist(matrix, vector):
    """
    Compute the cosine distances between each row of matrix and vector.
    """
    v = vector.reshape(1, -1)
    return scipy.spatial.distance.cdist(matrix, v, 'cosine').reshape(-1)