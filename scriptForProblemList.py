# This is a script based on matching with fuzzy logic,
# for comparing a list of descriptions with terms in SNOMED CT database.
import xlrd, xlwt
import pymysql
import os
import FuzzyMatch

def main():

    # set path to current directory
    current_path = os.path.abspath(__file__)
    os.chdir(os.path.dirname(current_path))

    print('Reading table...')
    excel1 = xlrd.open_workbook('Problem List.xlsx')
    table1 = excel1.sheet_by_name('data')
    refTermList = table1.col_values(2)[1:] # Column C without header

    print('Loading database...')
    rawData = connect_sql()
    data = [item['term'] for item in rawData]

    # build a dictionary where key is a word
    # and value is the set of all terms which has that word
    dict_Word_Terms = {}
    for term in data:
        wordList = FuzzyMatch.processTerm(term)
        for word in wordList:
            if word not in dict_Word_Terms.keys():
                dict_Word_Terms[word] = set()
            dict_Word_Terms[word].add(term)

    print('Start checking...')
    resultList = check_match(refTermList, dict_Word_Terms)

    print('Saving results...')
    save_results(resultList)


def connect_sql():

    try:
        conn = pymysql.connect(host='127.0.0.1',
                             user='root',
                             passwd='****',
                             db='NHS_dbo',
                             port=3306,
                             charset='utf8')

    except Exception as e:
        print("Fail to connect database:", e)

    else:
        # extract all disctinct terms that type is synonym
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = "SELECT DISTINCT term FROM NHS_dbo.description_activelist \
        where typeId='900000000000013009' "
        cur.execute(sql)
        rawData = cur.fetchall()
        # rawData = cur.fetchmany(1000)

        cur.close()
        conn.close()

    return rawData


def check_match(refTermList, dict_Word_Terms):

    EXACT_MATCH_RATIO = 1.1 # define a value larger than 1.0 to show exact match

    resultList = []

    for i, thisTerm in enumerate(refTermList):

        # preprocess this term as a list of key words
        wordList = FuzzyMatch.processTerm(thisTerm)

        # find a subset of terms in SNOMED CT database
        # that are related to this term
        correspondingTermSet = set()
        for word in wordList:
            if word in dict_Word_Terms.keys():
                correspondingTermSet.update(dict_Word_Terms[word])

        thisTupleList = []
        if thisTerm in correspondingTermSet:
            # exact match
            thisTuple = (thisTerm, EXACT_MATCH_RATIO)
            thisTupleList.append(thisTuple)
        elif len(correspondingTermSet) == 0:
            # no match
            thisTuple = ('',0) # match ratio is zero
            thisTupleList.append(thisTuple)
        else:
            for item in correspondingTermSet:
                # compared with each related terms
                thisLikehood = \
                FuzzyMatch.computeRatio_processed(thisTerm, item)
                thisTuple = (item,thisLikehood)
                thisTupleList.append(thisTuple)
        resultList.append(thisTupleList)

        if i%100 == 0:
            print('Progress:', i+1, '/', len(refTermList))

    return resultList


def save_results(resultList):

    # opening a new excel to save results
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('output_file')
    worksheet.write(0, 0, 'Fuzzy Match Ratio (MAX)')
    worksheet.write(0, 1, 'Fuzzy Match Ratio')
    worksheet.write(0, 2, 'Fuzzy Match Term')
    worksheet.write(0, 3, 'Note')

    for i, thisItem in enumerate(resultList):

        # set a threshold based on the maximum likehood
        likehoodMax = max([thisTuple[1] for thisTuple in thisItem])
        if likehoodMax >= 1.0:
            likehoodTh = 0.99
        elif likehoodMax > 0.4:
            likehoodTh = 0.4
        else:
            likehoodTh = 0
        # filter out the terms that are not above threshold
        candiTuples = [thisTuple for thisTuple in thisItem if thisTuple[1] > likehoodTh]
        # sorting by the ratio highest first
        candiTuples.sort(key=lambda temp: temp[1], reverse=True)

        # due to the row height limit in Excel,
        # only first 20 terms are shown.
        thisMsg = ''
        if len(candiTuples) > 20:
           thisMsg = 'Only 20' + '/' + str(len(candiTuples)) + ' shown due to space limit.'
           thisMsg = thisMsg + '\nLast Match Ratio: '+ str(candiTuples[-1][1])
           candiTuples = candiTuples[:20]

        candiLikehood = [str(round(thisTuple[1],2)) for thisTuple in candiTuples]
        candiTerms = [thisTuple[0] for thisTuple in candiTuples]

        worksheet.write(i+1, 0, str(round(likehoodMax,2)))
        worksheet.write(i+1, 1, '\n'.join(candiLikehood).strip())
        worksheet.write(i+1, 2, '\n'.join(candiTerms).strip())
        worksheet.write(i+1, 3, thisMsg)

    workbook.save('OUTPUT.xls')
    return None


if __name__ == '__main__':
    print('********** Scripts start. **********')
    main()
    print('********** Scripts end. **********')
