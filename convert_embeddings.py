import os
import numpy as np
import shelve
from utils import RESOURCE_PATH

def main():
    if os.path.isfile(RESOURCE_PATH['WORD_EMBEDDINGS']): return
    
    data = []
    for line in open(RESOURCE_PATH['WORD_EMBEDDINGS'].replace('.shelve', '.tsv'), encoding='utf-8'):
        data.append(line.strip().split('\t'))
    embeddings_dims = list(map(lambda x: len(x) - 1, data))
    embeddings_dim = max(set(embeddings_dims), key=lambda val: embeddings_dims.count(val))
    
    with shelve.open(RESOURCE_PATH['WORD_EMBEDDINGS']) as emb:
        for line in data:
            if len(line) - 1 == embeddings_dim:
                emb[line[0]] = np.array(line[1:]).astype(np.float16)
    

if __name__ == "__main__":
    main()
