import os
import numpy as np
from sqlitedict import SqliteDict
from utils import RESOURCE_PATH


def main():
    if os.path.isfile(RESOURCE_PATH['WORD_EMBEDDINGS'] + '*'):
        return

    data = []
    for line in open(RESOURCE_PATH['WORD_EMBEDDINGS'].replace('.sqlite', '.tsv'), encoding='utf-8'):
        data.append(line.strip().split('\t'))
    embeddings_dims = list(map(lambda x: len(x) - 1, data))
    embeddings_dim = max(set(embeddings_dims), key=lambda val: embeddings_dims.count(val))

    with SqliteDict(RESOURCE_PATH['WORD_EMBEDDINGS'], autocommit=True) as db:
        for line in data:
            if len(line) - 1 == embeddings_dim:
                db[line[0]] = np.array(line[1:]).astype(np.float32)

    print('Success!')


if __name__ == "__main__":
    main()
