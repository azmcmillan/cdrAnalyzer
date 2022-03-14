import pandas as pd
import datetime
#
# Gather details on what we're looking for
#



print('---------------------')
#calledNum = input('Enter the called number:')
calledNum = '2086253051'
#callingNum = input('Enter the calling number:')

csvFile = "exportData/cdr.csv"
csvData = pd.read_csv(csvFile, low_memory=False)
result = csvData[csvData['finalCalledPartyNumber']==calledNum]
#result['dateTimeOrigination'] = result['dateTimeOrigination'].apply(lambda x: pd.to_datetime(x, unit='s'))
result['dateTimeOrigination'] = pd.to_datetime(result['dateTimeOrigination'], unit='s', origin='unix')
#result.set_index('dateTimeOrigination',inplace=True)
result = result[['dateTimeOrigination', 'callingPartyNumber', 'finalCalledPartyNumber']]
result.groupby([result['dateTimeOrigination'].dt.day]).describe()

#groupDate = result.groupby(['dateTimeOrigination'])['dateTimeOrigination'].count()
#print(groupDate)

totalCalls = result.shape[0]

print('\n---- CDR RESULTS ----')
print('The called number ' + str(calledNum) + ' has been called ' + str(totalCalls) + ' times.')
print('---------------------')

for call in result.index:
    calling = result['callingPartyNumber'][call]
    called = result['finalCalledPartyNumber'][call]
    time = result['dateTimeOrigination'][call]
    #time = datetime.datetime.fromtimestamp(result['dateTimeOrigination'][call])
    print(str(time) + ': ' + calling + ' called ' + called)