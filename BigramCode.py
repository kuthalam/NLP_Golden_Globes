import json
import re
import time
import math
from nltk.corpus import stopwords

def bigramDetector(tweetData):
    start = time.time()
    words = dict()
    bigrams = dict()
    bigramCount = 0
    bigramsRet = 100 # How many bigrams to return

    for tweet in tweetData:
        sentence = tweet.split() # Split sentence into words
        cleanedSentence = list()

        # Remove the undesired punctuation from the strings
        for w in sentence:
            if len(w) > 0 and w[0].isupper():
                cleanedSentence.append(re.sub("\,|\.|\!|\?|\-|\'\:\;","",w))

        # Collect all the potential bigrams
        for i in range(len(cleanedSentence)):
            word = cleanedSentence[i]
            if len(word) > 0 and word[0].isupper():
                # For every legit word, record and add to its score
                if word not in words:
                    words[word] = 1
                else:
                    words[word] += 1
            if word < (len(cleanedSentence) - 1):
                if word not in bigrams:
                    bigrams[word] = dict() # For every word, we record its "partner"
                    bigrams[word]["count"] = 0
                if cleanedSentence[i + 1] not in bigrams[word]: # Freq of bigram
                    bigrams[word][cleanedSentence[i + 1]] = 1
                else:
                    bigrams[word][cleanedSentence[i + 1]] += 1
                bigrams[word]["count"] += 1
                bigramCount += 1

    # Clean out all the stopwords
    for w in stopwords:
        words.pop(w.upper(),None)
        words.pop(w, None)
        words.pop(w.capitalize(), None)

    # Now we get the top bigrams
    topBiGrams = list()
    lowestProb = 1
    for b in bigrams:
        for b2 in bigrams[b]:
            if b2 != 'count':
                gram = b + " " + b2
                prob = math.log(bigrams[b]['count']/bigramcount) + math.log(bigrams[b][b2]/bigrams[b]['count'])
                element = (gram, prob)
                topBiGrams.append(element)

    # Sort the top bigrams
    wordlist = list(words.items())
    wordlist.sort(key = lambda a: a[1])
    topBiGrams.sort(key = lambda a: a[1])
    print("Time Elapsed: " + str((time.time() - start)) + "seconds")
    return topBiGrams
