Works with just vanilla Python:

The command 'python goldenGlobesParser.py <year>' will open 'gg<year>.json' and outputs 'answers-<year>.txt' and 'answers-<year>.json'  

If you wish to use the autograder with additional years simply add the data file named:

gg<year>.json to the directory

and then add:

goldenGlobesParser.doOutPutToFiles(<year>)

after line 68 in pre_ceremony() of gg_api.py

