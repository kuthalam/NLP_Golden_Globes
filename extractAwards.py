import json
import time

start = time.time()
data = json.loads(open('gg2013.json').read())
tweets = []

for d in data:
    sentence = d['text'].split()
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
            if finalAwards.index(s) not in awardWordCount:
                awardWordCount[finalAwards.index(s)] = dict()
            for w in tCopy:
                if w not in awardWordCount[finalAwards.index(s)]:
                    awardWordCount[finalAwards.index(s)][w] = 1
                else:
                    awardWordCount[finalAwards.index(s)][w] = awardWordCount[finalAwards.index(s)][w] + 1
            
print(finalAwards[5])
sortedWordCount = list(awardWordCount[5].items())
sortedWordCount.sort(key = lambda a: a[1])
print(sortedWordCount)