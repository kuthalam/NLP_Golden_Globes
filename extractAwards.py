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
data = json.loads(open('gg2015.json').read())
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
hostGrams = dict()

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
    if "host" in t:
        if "next" not in t and "year" not in t:
            t2 = []
            for w in t:
                if w not in ["at","host","the","golden","globes","and"]:
                    t2.append(w)
            for i in range(len(t2) - 1):
                if i < len(t2) - 1:
                    twoGram = t2[i] + " " + t2[i+1]                
                    if twoGram in hostGrams:
                        hostGrams[twoGram] += 1
                    else:
                        hostGrams[twoGram] = 1
                if i < len(t2) - 2:
                    threeGram = t2[i] + " " + t2[i+1] + " " + t2[i+2]
                    if threeGram in hostGrams:
                        hostGrams[threeGram] += 1
                    else:
                        hostGrams[threeGram] = 1
   
def addWords(previous, word, container, p1, p2):
    if word.word == "END":
        container.append(previous)
    else:
        end = False 
        for s in word.successors:
            if s.word == "END" and s.count/word.count > p1:
                end = True
                addWords(previous + " " + word.word, s, container, p1, p2)
        if not end:
            for s in word.successors:
                if s.count/word.count > p2:
                    addWords(previous + " " + word.word, s, container, p1, p2)
wordList = []
addWords("", awards, wordList, 0.1, 0.01)
awardStrings2 = []
for w in wordList:
    awardStrings2.append(w[1:])

def bestGram(container):
    gram = ""
    max = 0
    maxWord = ""
    found = True
    while maxWord != "END" and found:
        max = 0
        maxWord = ""
        found = False
        total = 0
        for s in container:
            total = total + s.count
            if s.count > max:
                max = s.count
                maxWord = s.word
                maxContainer = s.successors
                found = True
        if maxWord != "END" and (max / total) > 0.4:
            gram = gram + " " + maxWord
        else:
            found = False
        container = maxContainer
    return gram 
    


awards = dict()
for t in bestTweets:
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
finalAwardGrams = []
finalAwardBestGram = []
finalAwardBestGrams = []
finalAwardNomineeGuesses = []
finalAwardPresenterGuess = []
# Test on single index:
for k in range(len(finalAwards)):
    phraseTree = []
    presenterGuesses = dict()
    nomineesGuesses = dict()
    sortedWordCount = list(awardWordCount[k].items())
    sortedWordCount.sort(key = lambda a: a[1])
    sortedWordCount2 = []
    for s in sortedWordCount:
        if s[0] != "for" and s[0] != "to" and s[0] != "win" and s[0] != "wins" and s[0] != "of" and s[0] != "goes" and s[0] != "the" and s[0] != "amp":
            sortedWordCount2.append(s)
    sortedWordCount = sortedWordCount2[len(sortedWordCount2) - 11 :]
    for t in awardTweets[k]:
        for token in sortedWordCount:
            if token[0] in t:
                current = None
                for s in phraseTree:
                    if s.word == token[0]:
                        current = s
                        current.count = current.count + 1
                if current == None:
                    word = wordNode(token[0])
                    phraseTree.append(word)
                    current = word
                i = t.index(token[0]) + 1
                end = False
                while i <= len(t) and end == False:
                    if i == len(t):
                        theWord = "END"
                        end = True
                    else:
                        theWord = t[i]
                    word = None
                    for s in current.successors:
                        if s.word == theWord:
                            word = s
                    if word == None:
                        word = wordNode(theWord)
                        current.successors.append(word)
                    word.count = word.count + 1
                    current = word
                    i = i + 1
        if "nominees" in t:
            for w in t:
                if w not in ["nominees","are","for","and","to","the"]:
                    t2.append(w)
                for i in range(len(t2) - 1):
                    twoGram = t2[i] + " " + t2[i+1]                
                    if twoGram in nomineesGuesses:
                        nomineesGuesses[twoGram] += 1
                    else:
                        nomineesGuesses[twoGram] = 1
        if "presenting" in t or "presenter" in t:
            for w in t:
                if w not in ["nominees","are","for","and","to","the","presenter","presenting"]:
                    t2.append(w)
                for i in range(len(t2) - 1):
                    twoGram = t2[i] + " " + t2[i+1]                
                    if twoGram in presenterGuesses:
                        presenterGuesses[twoGram] += 1
                    else:
                        presenterGuesses[twoGram] = 1
        


        
    
    phraseTree.sort(key = lambda a: a.count)
    bestGrams = []
    if len(phraseTree) > 0:
        bestGrams.append(phraseTree[-1].word + bestGram(phraseTree[-1].successors))
    if len(phraseTree) > 1:
        bestGrams.append(phraseTree[-2].word + bestGram(phraseTree[-2].successors))
    if len(phraseTree) > 2:
        bestGrams.append(phraseTree[-3].word + bestGram(phraseTree[-3].successors))
    
    
    semiFinalists = []

    for g in bestGrams:
        if " wins " in g:
            g = g[:g.index(" wins ")]
            semiFinalists.append(g)
        if " for " in g:
            g = g[:g.index(" for ")]
            semiFinalists.append(g)
        if " to " in g:
            g = g[g.index(" to ") + 4:]
            semiFinalists.append(g)

    if len(semiFinalists) == 0:
        for g in bestGrams:
            semiFinalists.append(g)

    finalists = dict()

    if len(semiFinalists) > 1:
        for i in range(len(semiFinalists)):
            substring = False
            for j in range(len(semiFinalists)):
                if semiFinalists[i] in semiFinalists[j] and not i == j:
                    substring = True
                    if semiFinalists[i] in finalists:
                        del finalists[semiFinalists[i]]
                    if semiFinalists[j] not in finalists:
                        finalists[semiFinalists[j]] = 2
                    else:
                        finalists[semiFinalists[j]] += 1
            if not substring:
                finalists[semiFinalists[i]] = 1
    else:
        finalists[semiFinalists[0]] = 3
    max = 0
    winner = ""
    for k in finalists:
        if finalists[k] > max:
            winner = k
            max = finalists[k]
    if winner == "":
        winner = bestGrams[0]

 
    nomineesGuesses = list(nomineesGuesses.items())
    nomineesGuesses.sort(key = lambda a: a[1])
    if len(nomineesGuesses) > 5:
        nomineesGuesses = nomineesGuesses[-5:][0]
    else:
        nomineesGuesses = []
    presenterGuesses = list(presenterGuesses.items())
    presenterGuesses.sort(key = lambda a: a[1])
    if len(presenterGuesses) > 0:
        presenterGuesses = presenterGuesses[-1][0]
    else:
        presenterGuesses = "Unknown"
 

    finalAwardNomineeGuesses.append(nomineesGuesses)
    finalAwardPresenterGuess.append(presenterGuesses)
    finalAwardBestGrams.append(bestGrams)
    finalAwardBestGram.append(winner)

    '''
    grams = []
    for s in phraseTree:
        addWords("",s,grams,0.3,0.6)
    finalAwardGrams.append(grams)
    '''

for k in range(len(finalAwards)):
    print("======================")
    print("Award: " + " ".join(finalAwards[k]))
    print("Winner: " + finalAwardBestGram[k])
    print("Candidates: " + ", ".join(finalAwardBestGrams[k]))
    print("Presenter: " + finalAwardPresenterGuess[k])
    print("Nominees: ")
    print(finalAwardNomineeGuesses[k])

hostGuesses = list(hostGrams.items())
hostGuesses.sort(key = lambda a: a[1])
print("=========================")
print("Host: " + hostGuesses[-1][0])


'''
for i in range(len(finalAwards)):           
    print(finalAwards[i])
    sortedWordCount = list(awardWordCount[i].items())
    sortedWordCount.sort(key = lambda a: a[1])
    print(sortedWordCount[len(sortedWordCount) - 11 :])
'''

print("Final Time Elapsed: " + str((time.time() - start)) + "seconds")