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
        result = csvData[csvData['finalCalledPartyNumber']==num]
        #result = csvData[csvData['finalCalledPartyNumber'].str.contains(num, regex=True)]

        # Strip all columns except the following
        result = result[['dateTimeOrigination', 'callingPartyNumber', 'finalCalledPartyNumber', 'globalCallID_callId', 'duration']]
        result['dateTimeOrigination'] = pd.to_datetime(result['dateTimeOrigination'], unit='s', origin='unix', utc=True)
        result['dateTimeOrigination'] = result['dateTimeOrigination'].dt.tz_convert('America/Los_Angeles')
        totalCallsSum = str(result.shape[0])

        print('\n')
        print('----     CDR RESULTS     ----')
        print('The called number ' + num + ' has been called ' + totalCallsSum + ' times.\n')
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

        result = result.sort_values(by='dateTimeOrigination')

        if uInput:
            print('\n----  INDIVIDUAL CALLS   ----')
            print('Timezone: America/Los_Angeles')
            print('dateTime, callId, duration, calling, called')

            for call in result.index:
                calling = result['callingPartyNumber'][call]
                called = result['finalCalledPartyNumber'][call]
                time = result['dateTimeOrigination'][call]
                callId = result['globalCallID_callId'][call]
                duration = result['duration'][call]
                print(f'{time}, {callId}, {duration}, {calling}, {called}')

    continueLookup = False
    ctLookupInput = input('\n\nWould you like to lookup another number? (y/n) ').lower()
    if ctLookupInput.startswith('y'): continueLookup = True

print('\n\nComplete...\n')