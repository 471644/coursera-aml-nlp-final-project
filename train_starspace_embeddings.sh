#!/usr/bin/env bash

MODELDIR=./data
DATADIR=./data

mkdir -p "${MODELDIR}"
mkdir -p "${DATADIR}"

echo "Start to train on Stack Overflow data:"

starspace train \
  -trainFile "${DATADIR}"/tagged_posts.tsv \
  -model "${MODELDIR}"/starspace_embeddings \
  -initRandSd 0.01 \
  -adagrad true \
  -ngrams 1 \
  -lr 0.01 \
  -epoch 5 \
  -thread 8 \
  -dim 100 \
  -negSearchLimit 10 \
  -trainMode 3 \
  -similarity "cosine" \
  -verbose true \
  -fileFormat labelDoc \
  -normalizeText 1 \
  -minCount 5
  
rm "${MODELDIR}"/starspace_embeddings
