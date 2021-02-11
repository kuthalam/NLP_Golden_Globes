# -*- coding: utf-8 -*-
'''Version 0.35'''
import json
import re
import string

from nltk.tokenize import wordpunct_tokenize

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

pre_ceremony_data = None
data_w_only_text = []
processed_data_w_text = []

punctuationToRemove = {"!", "?", "#", "@"}

# Mukund's Preprocessing utilities
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

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return "hosts"

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    # TODO: need to pre-process data
    global processed_data_w_text

    if not processed_data_w_text:
        pre_ceremony()

    awards_list = []
    awards_mention_reg_exp = "award\s|win\s"
    # r = re.compile(awards_mention_reg_exp)
    print("processed_data_w_text length: ", len(processed_data_w_text))
    tweetslist = [(idx, tweet) for idx, tweet in enumerate(processed_data_w_text)
                  if re.search(awards_mention_reg_exp, tweet)]

    # award_extraction_reg_exp = "(?:award|winner).*?for \"?(best[^\"\(\.]+)" # "(?:award|winner).*?for \"?([^\"\(]+)" # "(?:s|award|winner) for \"?([^\"\(]+)" # "award for \"?([^\"\(]+)"
    award_extraction_reg_exp = "wins (best[^\,\!\|\:\.]+(?=at|in|for)?)"
    for tweet_w_idx in tweetslist:
        # print("tweet: ", tweet_w_idx[1])
        awards_search = re.search(award_extraction_reg_exp, tweet_w_idx[1])
        if awards_search:
            awards_list.append(awards_search.group(1))
            # print("awards_search: ", awards_search.groups(1))

    awards_list = list(dict.fromkeys(awards_list))
    print("awards_list: \n", awards_list)
    return awards_list

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees = []
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners = []
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    presenters = []
    return presenters

# TODO: need to add a helper function to pass in years to process data

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")

    # Empty global variable (Is this a good idea to use global variable???)
    data_w_only_text = []
    pre_ceremony_data = None

    # the whole data is a huge list contains 174643 json objects.
    # all contains these keys {'timestamp_ms', 'text', 'user', 'id'}
    with open('/Users/cathylin/Desktop/CS-337/Project1/data/gg2013.json') as f:
        pre_ceremony_data = json.load(f)
        print('length of json data: ', len(pre_ceremony_data))

    # Only extract the text part, since that is relevant, and write to new file
    with open("formatted_gg2013_text.txt", 'w') as file:
        for data_obj in pre_ceremony_data:
            data_w_only_text.append(data_obj['text'])
            # print("data -> ", data_obj['text'])
            file.write(data_obj['text']+"\n")

    # Only text part with json format to help better visualization, need to comment out before submitting
    count = 0
    data_w_only_text_json = {}
    with open("formatted_gg2013_text.json", 'w') as file:
        for data_obj in pre_ceremony_data:
            data_w_only_text_json[count] = data_obj['text']
            count += 1

        json.dump(data_w_only_text_json, file, indent=4)

    # Utilize pre-processing utilities
    global processed_data_w_text
    processed_data_w_text = []
    for data in data_w_only_text:
        processedTweet = retweetPhraseRemover(data.lower())
        processedTweet = puncRemover(processedTweet)
        processedTweet = deEmojify(processedTweet)
        if not isEnglish(processedTweet):
            continue

        # remove beginning & end spaces
        processedTweet = processedTweet.strip()
        if processedTweet == "":
            continue
        processed_data_w_text.append(processedTweet)

    with open("processed_gg2013_tweet_text.txt", 'w') as file:
        for data in processed_data_w_text:
            file.write(data+"\n")

    # print(data_w_only_text[174606])

    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    pre_ceremony()
    get_awards(2013)
    return

if __name__ == '__main__':
    main()
