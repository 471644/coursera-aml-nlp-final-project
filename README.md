# [Final project](https://www.coursera.org/learn/language-processing/peer/xbHJG/stackoverflow-assistant) for Coursera Advanced ML specialization, [NLP course](https://www.coursera.org/learn/language-processing/home/welcome)

Stack Overflow assistant and chit-chat [bot](http://t.me/tQTZwetd_bot) for Telegram.

## Solution

### Assistant part

For both *Intent recognizer* (0.98403 accuracy) and *Tag classifier* (0.78565 accuracy) used ```LogisicRegression``` on ```HashingVectorizer``` features. For most similar thread retrieval I pretrained ```StarSpace``` embeddings and used unweighted sum over words embeddings for text summarization. Most similar thread taken by least cosine distance between summarized texts.

### Chit-chat part ([honor](https://www.coursera.org/learn/language-processing/peer/Tz9WP/custom-conversational-model))

For chit-chat model used seq2seq approach on chars level. Model implemented used Keras with Tensorflow backend and consist of single Embeddings, GRU and Dense layers. Dye to environment constraints I tried to choose hyper-parameters and training techniques to train model as small as possible. Therefore, I used single shared GRU layer with 384 units and input length of 32 for both encoder and decoder parts. To keep model capacity unconstrained I decided to avoid any explicit regularization (dropout, weight decay and etc), except additional language modelling task for encoder, which, I believe, also supposed to give useful gradients for early steps of encoding.

As dataset I used [Cornell Movie Dialogs](http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html).

Dialog example:

```
You:Hello!
Bot: Hello, sweetheart.
You:How are you?
Bot: Fine. You like it.
You:What is your name?
Bot: My name is Miles.
You:How old are you?
Bot: Fine.
You:How tall are you?
Bot: Fine.
You:Do you like me?
Bot: Yes, you do recall.
You:Did you enjoy your training schedule?
Bot: Want to take a dollar wearon?
You:I will consider it as positive answer
Bot: Accident.
You:exit
Bot: Please.
```

### Optimization

Early bot setup (even without chit-chat model) consumed a lot of RAM (about >1.2GB), so I found next techniques crucial to run service on weak machine:

1. Set environment variable ```OMP_NUM_THREADS = 1```, because by default numpy tries to run 4 threads, which multiplies RAM usage by 4.
2. Change proposed ```sklearn.metrics.pairwise_distances_argmin``` to ```scipy.spatial.distance.cdist```, because import of sklearn function pulls a lot of garbage with it.
3. Storing StarSpace embeddings in ```shelve``` format on disk.
4. Change proposed ```TfidVectorizer``` features to ```HashingVectorizer``` and set number of features 2 ^ 16 (instead 2 ^ 20 by default). ```TfidVectorizer``` holds necessary data in python dict which is memory inefficent and in same time ```HashingVectorizer``` requires no additional data at all.
5. Get rid of proposed ```OneVsRest``` classifier.
6. Save stopwords from ```nltk``` in pickle -- ```nltk``` is heavy library.

## Deploying
### Prerequisites
I chose Google Cloud f1-micro (1 vCPU, 0.6 GB memory) instance with minimized Ubuntu 16.04 LTS.

### Intallation
Run the following commands in your fresh VM instance's terminal:

```
  sudo apt-get update

  sudo apt-get install software-properties-common curl
  sudo add-apt-repository ppa:git-core/ppa
  curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
  sudo apt-get install git git-lfs
  git lfs install

  sudo apt-get install tmux apt-transport-https python3-pip
  
  git clone https://github.com/vBLFTePebWNi6c/coursera-aml-nlp-final-project.git
  cd coursera-aml-nlp-final-project
  sh deploy.sh
  sudo service telegram_bot start
```
