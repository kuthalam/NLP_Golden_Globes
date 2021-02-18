import json
import time
import re
import string


def puncRemover(str):
    for punc in punctuationToRemove:
        if punc in str:
            # Remove the punctuation and any charas next to it until a space
            if punc == "?": # Because question marks cause regex issues
                str = str.replace(punc, "")
            else:
                str = re.sub(punc + "!.*?\s", "", str) # Question: I don't understand why we should remove until a space?
                # feels like it will delete some things might be useful for sentiment analysis or so?
    return str

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def retweetPhraseRemover(str):
    # Question: I feel this will delete too much information,
    # therefore I changed the re to be have more constraints
    newStr = re.sub("https?:?([^\s]+)", "", str)
    newStr = re.sub("(?i)RT.*@\w*:\s", "", newStr)
    # Also remove tag starts with # or @, it should happen after removing retweet
    return re.sub("[#|@]\w+", "", newStr)




start = time.time()
data = json.loads(open('gg2013.json').read())
tweets = []

for d in data:
    sentence = retweetPhraseRemover(d['text'])
    sentence = sentence.split()
    s = []
    for w in sentence:
        if w[0:4] != "http":
            w2 = ""
            for c in w:
                if c.isalpha() or c in ['#','@']:
                    w2 += c.lower()
            if w2 != "":
                s.append(w2)
    tweets.append(s)
print("Pre-Processing Time Elapsed: " + str((time.time() - start)) + "seconds")

class wordNode:
    def __init__(self, word):
        self.word = word
        self.successors = []
        self.count = 1

awards = wordNode("best")

bestTweets = []

for t in tweets:
    if "best" in t:
        bestTweets.append(t)
        current = awards
        i = t.index("best") + 1
        end = False
        while i <= len(t) and end == False:
            if i == len(t) or t[i][0] == "#" or t[i][0] == "@" or t[i] == "for" or t[i] == "goes" or t[i] == "at" or t[i] == "is":
                theWord = "END"
                end = True
            else:
                theWord = t[i]
            current.count = current.count + 1
            word = None
            for s in current.successors:
                if s.word == theWord:
                    word = s
            if word == None:
                word = wordNode(theWord)
                current.successors.append(word)
            if word.word == "END":
                word.count = word.count + 1
            current = word
            i = i + 1
        
def addWords(previous, word, container):
    if word.word == "END":
        container.append(previous)
    else:
        end = False 
        for s in word.successors:
            if s.word == "END" and s.count/word.count > 0.1:
                end = True
                addWords(previous + " " + word.word, s, container)
        if not end:
            for s in word.successors:
                if s.count/word.count > 0.01:
                    addWords(previous + " " + word.word, s, container)
wordList = []
addWords("", awards, wordList)
awardStrings2 = []
for w in wordList:
    awardStrings2.append(w[1:])


awards = dict()
for t in tweets:
    if "best" in t:
        g = 9999
        for ender in ["goes"]:
            if ender in t:
                i = t.index(ender)
                if i < g:
                    g = i
        if g != 9999:
            b = t.index("best")
            phrase = ""
            if b < g:
                for i in range(b,g):
                    phrase = phrase + " " + t[i]
                if phrase in awards:
                    awards[phrase] = awards[phrase] + 1
                else:
                    awards[phrase] = 1

awardsList = list(awards.items())
awardsList.sort(key = lambda a: a[1])
awardStrings = []

for i in awardsList[len(awardsList) - 100: ]:
    awardStrings.append(i[0][1:])

semiFinalAwards = []

for a in awardStrings:
    if a in awardStrings2:
        semiFinalAwards.append(a.split())

finalAwards = []
for a1 in semiFinalAwards:
    add = True
    for a2 in semiFinalAwards:
        if a1 != a2 and len(a1) < len(a2):
            contains = True
            for a in a1:
                if a not in a2:
                    contains = False
            if contains:
                add = False
    if add:
        for a3 in finalAwards:
            contains = True
            for a in a1:
                if a not in a3:
                    contains = False
            if contains:
                add = False
    if add:
        finalAwards.append(a1)
print(finalAwards)
print("Time Elapsed: " + str((time.time() - start)) + "seconds")

awardWordCount = dict()
awardTweets = dict()

awardWords = []
for x in finalAwards:
    for w in x:
        if w not in awardWords:
            awardWords.append(w)

for t in bestTweets:
    for s in finalAwards:
        tContainsS = True
        tCopy = t.copy()
        for w in s:
            if w not in t:
                tContainsS = False
                break
            else:
                tCopy.remove(w)
        if tContainsS:
            tCopy2 = []
            for w in tCopy:
                if w not in awardWords:
                    tCopy2.append(w)
            tCopy = tCopy2
            if finalAwards.index(s) not in awardWordCount:
                awardWordCount[finalAwards.index(s)] = dict()
            for w in tCopy:
                if w not in awardWordCount[finalAwards.index(s)]:
                    awardWordCount[finalAwards.index(s)][w] = 1
                else:
                    awardWordCount[finalAwards.index(s)][w] = awardWordCount[finalAwards.index(s)][w] + 1
            if finalAwards.index(s) not in awardTweets:
                awardTweets[finalAwards.index(s)] = []
            awardTweets[finalAwards.index(s)].append(tCopy)



for i in range(len(finalAwards)):           
    print(finalAwards[i])
    sortedWordCount = list(awardWordCount[i].items())
    sortedWordCount.sort(key = lambda a: a[1])
    print(sortedWordCount[len(sortedWordCount) - 11 :])