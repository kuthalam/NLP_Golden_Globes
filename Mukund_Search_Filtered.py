# Project experimentation stuff

###### Resources that I looked at:
# IMDbPY and its docs: https://imdbpy.github.io/
# For string.ascii_letters: https://docs.python.org/3/library/string.html
# For string.replace(): https://www.tutorialspoint.com/python/string_replace.htm
# For regular expressions: https://docs.python.org/3/library/re.html
# List of NLTK POS tag meanings: https://medium.com/@gianpaul.r/tokenization-and-parts-of-speech-pos-tagging-in-pythons-nltk-library-2d30f70af13b
# Reading JSON from a file: https://www.programiz.com/python-programming/json
# Numpy documentation: https://numpy.org/doc/1.20/

OFFICIAL_AWARDS_1819 = ['best motion picture', 'best performance by an actress', 'best actress', 'best performance by an actor', 'best actor', 'best director',
'best screenplay', 'best motion picture', 'best foreign film', 'best original score', 'best original song', 'best television series', 'best tv series',
'cecil b. demille award']

###### Library imports
import json
import numpy as np
import time
import nltk
import re
import string
import math
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
from nltk.metrics.distance import edit_distance
from imdb import IMDb, IMDbError
import pandas as pd

###### Globals
winnerKeywords = {"won": "left", "goes to": "right"}
awardKeywords = {"award for": "right"}
nomineeKeywords = {"nominee": "right", "nominated": "left"}
punctuationToRemove = {"!", "?", "#", "@"}
peopleNames = set(pd.read_csv("Databases/name.basics.tsv", error_bad_lines = False, warn_bad_lines = False, sep="\t", low_memory = False)["primaryName"])
movieNames = set(pd.read_csv("Databases/title.akas.tsv", error_bad_lines = False, warn_bad_lines = False, sep="\t")["title"])

# Preprocessing utilities

#############################################################
# Name: puncRemover                                         #
# Params: givenStr                                          #
# Notes: Remove certain punctuation from given string.      #
#############################################################
def puncRemover(givenStr):
    for punc in punctuationToRemove:
        if punc in givenStr:
            if punc == "?": # Because question marks cause regex issues
                givenStr = givenStr.replace(punc, "")
            else:
                givenStr = re.sub(punc + ".*\s", "", givenStr)
    return givenStr

#############################################################
# Name: emojiRemover                                        #
# Params: givenStr                                          #
# Notes: Removes emojis from given string.                  #
#############################################################
def emojiRemover(givenStr):
    newStr = ""
    for word in wordpunct_tokenize(givenStr):
        if word.isalpha():
            newStr = newStr + word + " "
    return newStr

#############################################################
# Name: foreignLangDetector                                 #
# Params: givenStr                                          #
# Notes: Checks if the given string has any non-English     #
# charas.                                                   #
#############################################################
def foreignLangDetector(givenStr):
    for word in givenStr:
        for chara in word:
            if chara not in string.ascii_letters and not(chara == " ") and \
            not(chara == "\n"):
                return True
    return False

#############################################################
# Name: retweetPhraseRemover                                #
# Params: givenStr                                          #
# Notes: Removes all traces of retweets from the given      #
# string.                                                   #
#############################################################
def retweetPhraseRemover(givenStr):
    newStr = re.sub("http:.*", "", givenStr)
    newStr = re.sub("RT.*@\w*\s*:\s", "", newStr)
    return newStr

#############################################################
# Name: multiCharaFilter                                    #
# Params: givenWord                                         #
# Notes: Checks if the given string is something like       #
# "Aaaah" or "yaaaay".                                      #
#############################################################
def multiCharaFilter(givenWord):
    # First need to split a string into characters
    charaArr = re.split("\W*", givenWord)
    charaArr = charaArr[1:len(charaArr)-1] # Get rid of spaces

    # Get me all the counts of each character
    # The idea is to filter out all the phrases like "whoohoo" or "yeeeees"
    charaCounts = np.unique(charaArr, return_counts = True)[1]
    if len(np.where(charaCounts > 2)[0] > 0):
        return True
    return False

# Experiment Ideas:
#############################################################
# Name: keywordSearch                                       #
# Params: tweetData (tweet data from given json)            #
# guide (the specified set of keywords along with which     #
# half of the tweet to preserve if I find that word).       #
# Notes: Returns all tweets that have the keyword,          #
# specifically that part of the tweet with relevant info.   #
#############################################################
def keywordSearch(tweetData, guide):
    start_time = time.time()
    # First set up a dictionary of the tweets that correspond to each keyword
    relevantTweets = set() # Unlikely that any two tweets would be identical
    allKeywords = list(guide.keys()) # All the keywords to search for

    for tweet in tweetData:
        # Preprocess each tweet
        processedTweet = retweetPhraseRemover(tweet["text"])
        processedTweet = puncRemover(processedTweet)
        processedTweet = emojiRemover(processedTweet)
        if foreignLangDetector(processedTweet):
            continue

        # Check if the tweet has a keyword
        for word in guide:
            if word in processedTweet:
                if guide[word] == "left":
                    relevantTweets.add(processedTweet[:processedTweet.index(word)])
                else:
                    startIdx = processedTweet.index(word) + len(word) + 1
                    relevantTweets.add(processedTweet[startIdx:])

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time for keyword search: " + str(total_time))
    return relevantTweets

#############################################################
# Name: properNounFinder                                    #
# Params: tweetData (tweet data from given json)            #
# Notes: Returns the proper nouns (i.e. names) in the       #
# tweet data. Main pre-DB search bottleneck.                #
#############################################################
def properNounFinder(tweetData):
    start_time = time.time()
    candidates = set()
    for tweet in tweetData:
        # First some pre-processing
        processedTweet = retweetPhraseRemover(tweet["text"])
        processedTweet = puncRemover(processedTweet)
        processedTweet = emojiRemover(processedTweet)
        if foreignLangDetector(processedTweet):
            continue

        # Next some tagging
        tokenizedTweet = nltk.word_tokenize(processedTweet)
        taggedTweet = nltk.pos_tag(tokenizedTweet)

        for tagPair in taggedTweet:
            if tagPair[1] == "NNP":
                candidates.add(tagPair[0].lower()) # Need this for comparison
    end_time = time.time()
    total_time = end_time - start_time
    print("Total time for proper noun finder: " + str(total_time))
    return candidates

#############################################################
# Name: awardTweetFinder                                    #
# Params: tweetData (tweet data from given json)            #
# Notes: Returns the proper nouns (i.e. names) in the       #
# tweet data. Main pre-DB search bottleneck.                #
#############################################################
def awardTweetFinder(tweetData):
    start_time = time.time()
    usefulTweets = set()
    for tweet in tweetData:
        # First some pre-processing
        processedTweet = retweetPhraseRemover(tweet["text"])
        processedTweet = puncRemover(processedTweet)
        processedTweet = emojiRemover(processedTweet)
        if foreignLangDetector(processedTweet):
            continue

        # Then we filter down to the tweets that mention the awards
        for award in OFFICIAL_AWARDS_1819:
            if award in processedTweet:
                usefulTweets.add(processedTweet)

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time for award tweet finder: " + str(total_time))
    return usefulTweets

#############################################################
# Name: ngramDetector (mostly adapted from Leif's code)     #
# Params: tweetData (tweets that were filtered through the  #
# award tweet rule)                                         #
# Notes: Returns the proper nouns (i.e. names) in the       #
# tweet data. Main pre-DB search bottleneck.                #
#############################################################
def ngramDetector(tweetData):
    start = time.time()
    words = dict()
    bigrams = dict()
    bigramCount = 0
    ngramsRet = 50 # How many ngrams to return

    for tweet in tweetData:
        sentence = tweet.split() # Split sentence into words
        cleanedSentence = list()

        # Remove the undesired punctuation from the strings
        for w in sentence:
            if len(w) > 0 and w[0].isupper():
                cleanedSentence.append(re.sub("\,|\.|\!|\?|\-|\'\:\;","",w))
            else:
                cleanedSentence.append(w)

        # Collect all the potential bigrams
        for i in range(len(cleanedSentence)):
            word = cleanedSentence[i]
            if len(word) > 0 and word[0].isupper():
                # For every legit 1-gram, collect it and add to its score
                if word not in words:
                    words[word] = 1
                else:
                    words[word] += 1
            if i < (len(cleanedSentence) - 1):
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
    for w in stopwords.words("english"):
        words.pop(w.upper(),None)
        words.pop(w, None)
        words.pop(w.capitalize(), None)

    # Now we get the top bigrams
    topBigrams = list()
    lowestProb = 1
    for b in bigrams:
        for b2 in bigrams[b]:
            if b2 != 'count':
                gram = b + " " + b2
                prob = math.log(bigrams[b]['count']/bigramCount) + math.log(bigrams[b][b2]/bigrams[b]['count'])
                element = (gram, prob)
                topBigrams.append(element)

    # Sort the top bigrams
    wordList = list(words.items())
    wordList.sort(key = lambda a: a[1], reverse=True)
    topBigrams.sort(key = lambda a: a[1], reverse=True)
    print("Total time for Bigram Search: " + str((time.time() - start)) + " seconds")
    return wordList[:ngramsRet], topBigrams[:ngramsRet]

#############################################################
# Name: databaseSearcher                                    #
# Params: resultsSoFar (from the resultCombiner)            #
# category (for which we are searching for names)           #
# database (the IMDb object)                                #
# potentialWinners (the set of names to look for)           #
# Notes: Search and return names from the IMDb database     #
# that correspond to the proper nouns that we decided to    #
# work with.                                                #
#############################################################
def databaseSearcher(resultsSoFar, category, database):
    start_time = time.time()

    # First we need just the unigrams, not the vote counts
    ngramStrings = [result[0] for result in resultsSoFar]

    finalAnswer = set() # List of all the people/movies
    searchCounter = 0

    # Now we need two sets - one for single name movies and another for multi-name
    confirmedNames = set() # The final set of guesses
    goodSearchResults = list() # Good search results from IMDb

    for result in ngramStrings:
        if "winner" in category or "nominee" in category:
            try:
                # Since we don't know if any given word corresponds to a movie
                # or person, we search for both.
                for searchResult in peopleNames:
                    if edit_distance(result, str(searchResult)) < 2:
                        print(result)
                        print(searchResult)
                        goodSearchResults.append(searchResult.lower())
                for searchResult in movieNames:
                    if result in str(searchResult):
                        print(result)
                        print(searchResult)
                        goodSearchResults.append(searchResult.lower())
                searchCounter += 1
                print("Completed " + str(searchCounter) + " searches of " + str(len(resultsSoFar)) + " total.")
                print(len(goodSearchResults))
            except IMDbError as e:
                print("Something went wrong with the search. Moving on to the next one.")

    # Now that we have all the search results
    if "winner" in category or "nominee" in category:
        # Idea is that if we have "Ben" and "Affleck" as separate entries,
        # we will find both names when we search each entry on its own
        # All such situations correspond to count > 1
        uniqueValues = np.unique(goodSearchResults, return_counts = True)
        uniqueNames = uniqueValues[0] # All the unique names
        nameOccurrenceCounts = uniqueValues[1] # How many times they occurred
        confirmedNames = set(uniqueNames[np.where(uniqueValues[1] > 1)])

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time for database search: " + str(total_time))
    return confirmedNames

#############################################################
# Name: main                                                #
# Params: None                                              #
# Notes: Just putting it all together.                      #
#############################################################
def main():
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')
    with open("gg2013.json") as tweetData:
        data = json.load(tweetData)
        imdbObj = IMDb()
        print()
        print("The winners:")
        relevantTweets = keywordSearch(data, winnerKeywords)
        topUnigrams, topBigrams = ngramDetector(relevantTweets)

        # This is the final set of people
        relevantNgrams = list()
        relevantNgrams.extend(topUnigrams)
        relevantNgrams.extend(topBigrams)
        print(databaseSearcher(relevantNgrams, "winner", imdbObj))
        # print()
        # print()
        # print("The nominees:")
        # relevantTweets = keywordSearch(data, nomineeKeywords)
        # topUnigrams, topBigrams = ngramDetector(relevantTweets)
        #
        # # This is the final set of people
        # relevantNgrams = list()
        # relevantNgrams.extend(topUnigrams)
        # relevantNgrams.extend(topBigrams)
        # print(databaseSearcher(relevantNgrams, "nominees", imdbObj))

if __name__ == "__main__":
  main()
