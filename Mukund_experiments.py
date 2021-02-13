# Project experimentation stuff

###### Resources that I looked at:
# IMDbPY and its docs: https://imdbpy.github.io/
# For string.ascii_letters: https://docs.python.org/3/library/string.html
# For string.replace(): https://www.tutorialspoint.com/python/string_replace.htm
# For regular expressions: https://docs.python.org/3/library/re.html
# List of NLTK POS tag meanings: https://medium.com/@gianpaul.r/tokenization-and-parts-of-speech-pos-tagging-in-pythons-nltk-library-2d30f70af13b
# Reading JSON from a file: https://www.programiz.com/python-programming/json
# Numpy documentation: https://numpy.org/doc/1.20/

###### Library imports
import json
import numpy as np
import time
import nltk
import re
import string
from nltk.tokenize import wordpunct_tokenize
from imdb import IMDb, IMDbError

###### Globals
winnerKeywords = {"won": "left", "goes to": "right"}
awardKeywords = {"award for": "right"}
nomineeKeywords = {"nominee": "right", "nominated": "left"}
punctuationToRemove = {"!", "?", "#", "@"}

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
    relevantTweets = dict() # Unlikely that any two tweets would be identical
    allKeywords = list(guide.keys()) # All the keywords to search for

    # Sets up a dictionary for collecting and maintaining relevant tweets
    for word in guide:
        relevantTweets[word] = set()

    for tweet in tweetData:
        # Preprocess each tweet
        processedTweet = retweetPhraseRemover(tweet["text"])
        processedTweet = puncRemover(processedTweet.lower())
        processedTweet = emojiRemover(processedTweet)
        if foreignLangDetector(processedTweet):
            continue

        # Check if the tweet has a keyword
        for word in guide:
            if word in processedTweet:
                if guide[word] == "left":
                    relevantTweets[word].add(processedTweet[:processedTweet.index(word)])
                else:
                    relevantTweets[word].add(processedTweet[processedTweet.index(word):])

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
# Name: resultCombiner                                      #
# Params: usefulTweets (tweets with keyword)                #
# potentialWinners (the set of names to look for)           #
# Notes: Returns the proper nouns that were found in tweets #
# with keywords.                                            #
#############################################################
def resultCombiner(usefulTweets, potentialWinners):
    start_time = time.time()
    likelyCand = set()
    for word in usefulTweets.keys(): # For each keyword used to filter the tweets
        currentSet = usefulTweets[word]
        prunedSet = set()

        # Check if some of the proper nouns from before are in each tweet.
        # Collect the proper nouns that satisfy this
        for tweet in currentSet:
            for winner in potentialWinners:
                if winner in tweet:
                    prunedSet.add(winner)

        # Now we collect all of these candidates. The "voting" happens
        # when we search the database.
        likelyCand = likelyCand.union(prunedSet) # Helps avoid reference issues

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time for result combiner: " + str(total_time))
    return likelyCand

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

    # First some search preprocessing
    # Let's try filtering out the words that are like "whoohoo" or "yeeees"
    for word in resultsSoFar:
         if multiCharaFilter(word):
             resultsSoFar = resultsSoFar.difference({word})

    finalAnswer = set() # List of all the people/movies
    searchCounter = 0

    # Now we need two sets - one for single name movies and another for multi-name
    confirmedNames = set() # The final set of guesses
    allSearchResults = list() # All search results from IMDb

    for result in resultsSoFar:
        if "winner" in category or "nominee" in category:
            try:
                # Since we don't know if any given word corresponds to a movie
                # or person, we search for both.
                for searchResult in database.search_person(result):
                    allSearchResults.append(str(searchResult).lower())
                for searchResult in database.search_movie(result):
                    allSearchResults.append(str(searchResult).lower())
                searchCounter += 1
                print("Completed " + str(searchCounter) + " searches of " + str(len(resultsSoFar)) + " total.")
            except IMDbError as e:
                print("Something went wrong with the search. Moving on to the next one.")

    # Now that we have all the search results
    if "winner" in category or "nominee" in category:
        # Idea is that if we have "Ben" and "Affleck" as separate entries,
        # we will find both names when we search each entry on its own
        # All such situations correspond to the count > 1
        uniqueValues = np.unique(allSearchResults, return_counts = True)
        uniqueNames = uniqueValues[0] # All the unique names
        nameOccurrenceCounts = uniqueValues[1] # How many times they occurred
        confirmedNames = set(uniqueNames[np.where(uniqueValues[1] > 1)])

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time for result combiner: " + str(total_time))
    return confirmedNames

#############################################################
# Name: main                                                #
# Params: None                                              #
# Notes: Just putting it all together.                      #
#############################################################
def main():
    nltk.download('averaged_perceptron_tagger')
    with open("gg2013.json") as tweetData:
        data = json.load(tweetData)
        imdbObj = IMDb()
        # print()
        # print("All the winners:")
        # parsedResults = resultCombiner(keywordSearch(data, winnerKeywords), properNounFinder(data))
        #
        # # This is the final set of people
        # print(databaseSearcher(parsedResults, "winner", imdbObj))
        # print()
        print()
        print("The nominees:")
        parsedResults = resultCombiner(keywordSearch(data, nomineeKeywords), properNounFinder(data))

        # This is the final set of people
        print(databaseSearcher(parsedResults, "nominees", imdbObj))

if __name__ == "__main__":
  main()
