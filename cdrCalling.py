import pandas as pd

print('---------------------\n')
print('Use this tool to search through exported CDR data from Call Manager.\n')
print('CDR DATA INSTRUCTIONS:')
print('  1. Confirm your exported CDR data is placed in the "exportData" folder.')
print('  2. Rename your CDR data file to "cdr.csv"\n')
print('SEARCHING INSTRUCTIONS:')
print('  It is important NOT to include - or . characters in your number search.')
print('  For example searching for 208-625-5555... you would use 2086255555.\n')
print('  To search for more than one number, use a comma seperate list.')
print('  Example: 2086251234,2086252345,2086253456\n')
print('---------------------')

continueLookup = True
while(continueLookup):
    # Gather number(s) to search for.
    callNum = []
    uNumLookup = input('\nPlease enter the called number in the format XXXXXXXXXX:')
    callNum = uNumLookup.split(',')

    csvFile = "exportData/cdr.csv"
    csvData = pd.read_csv(csvFile, low_memory=False)
    csvData['callingPartyNumber'] = csvData['callingPartyNumber'].apply(str)
    csvData['finalCalledPartyNumber'] = csvData['finalCalledPartyNumber'].apply(str)

    for num in callNum:
        num = str(num)
        # Search through CSV data for called party number.
        #result = csvData[csvData['finalCalledPartyNumber']==num]
        result = csvData[csvData['finalCalledPartyNumber'].str.contains(num, regex=True)]

        # Strip all columns except the following
        result = result[['dateTimeOrigination', 'callingPartyNumber', 'finalCalledPartyNumber']]
        result['dateTimeOrigination'] = pd.to_datetime(result['dateTimeOrigination'], unit='s', origin='unix')
        totalCallsSum = str(result.shape[0])

        print('\n')
        print('----     CDR RESULTS     ----')
        print('The calling number ' + num + ' has made ' + str(totalCallsSum) + ' phone calls.\n')
        print('---- TOTAL CALLS PER-DAY ----')
        print('dateTime, totalCalls')

        #Calculate the total calls for the called number by date
        datez = pd.to_datetime(result['dateTimeOrigination'], unit='s', origin='unix')
        totalCalls = datez.groupby(datez.dt.floor('d')).size().reset_index(name='count')

        for date in totalCalls.index:
            todaysDate = totalCalls['dateTimeOrigination'][date]
            todaysCount = totalCalls['count'][date]
            print(todaysDate.strftime('%Y-%m-%d') + ', ' + str(todaysCount))

        uInput = False
        x = input('\nWould you like to see all calls? (y/n) ').lower()
        if x.startswith('y'): uInput = True

        if uInput:
            print('\n----  INDIVIDUAL CALLS   ----')
            print('dateTime, calling, called')

            for call in result.index:
                calling = result['callingPartyNumber'][call]
                called = result['finalCalledPartyNumber'][call]
                time = result['dateTimeOrigination'][call]
                print(str(time) + ', ' + calling + ', ' + called)
    
    continueLookup = False
    ctLookupInput = input('\n\nWould you like to lookup another number? (y/n) ').lower()
    if ctLookupInput.startswith('y'): continueLookup = True

print('\n\nComplete...\n')