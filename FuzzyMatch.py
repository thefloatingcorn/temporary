# Methods defined for fuzzy match
# version 1.1.0
# updated 20190809

def computeRatio_processed(processedTerm1, processedTerm2):
    # input type: string, string
    # output type: float

    # should be used only if both terms have been preprocessed
    # by the method processTerm(), for improving speed

    insection = set(processedTerm1) & set(processedTerm2)
    likehood = len(insection) / max(len(set(processedTerm1)),len(set(processedTerm2)))

    return likehood


def computeRatio(term1, term2):
    # input type: string, string
    # output type: float

    processedTerm1 = processTerm(term1)
    processedTerm2 = processTerm(term2)

    # the likehood ratio is calculated on the basis of their intersection words
    insection = set(processedTerm1) & set(processedTerm2)
    likehood = len(insection) / max(len(set(processedTerm1)),len(set(processedTerm2)))

    return likehood


def processTerm(term):
    # input type: string
    # output type: list of strings

    term = term.lower()
    wordList = removeSpecialChar(term)
    processedWordList = removeSpecialWord(wordList)

    return processedWordList


def removeSpecialChar(term):
    # input type: string
    # output type: list of strings

    # remove without leaving space
    specialCharList1 = ['"', "+", "+/-", "&", "(", ")", ","]
    for sc in specialCharList1:
        term = term.replace(sc, "")

    # remove but leaving space
    specialCharList2 = [" - ", " / ", "/", "  "]
    for sc in specialCharList2:
        term = term.replace(sc, " ")

    wordList = term.split(' ')

    return wordList


def removeSpecialWord(wordList):
    # input type: list of strings
    # output type: list of strings

    updatedList = []
    specialWordSet = defineSpecialWord()
    for word in wordList:
        if (word not in specialWordSet) and (len(word)!=0):
            updatedList.append(word)

    return updatedList


def defineSpecialWord():
    # output type: set of strings

    specialWordList = []
    specialWordList += ['and', 'or', 'with', 'of', 'from', 'to', 'using',
                    'due', 'in', 'for']
    specialWordList += ['test', 'treatment', 'examination','surgery',
                    'operation','procedure','approach', 'lesion']
    specialWordList += ['left', 'right', 'bilateral', 'unilateral','yes/no','space']
    specialWordList += ['- uclh historical lab','uclh']

    specialWordSet = set(specialWordList)

    return specialWordSet
