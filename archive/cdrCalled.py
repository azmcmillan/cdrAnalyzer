import pandas as pd
#pd.option_context('display.max_colwidth', None, 'display.max_columns', None, 'display.max_rows', None)
pd.options.mode.chained_assignment = None  # default='warn'

print('---------------------\n')
print('Use this tool to search through exported CDR data from Call Manager.\n')
print('CDR DATA INSTRUCTIONS:')
print('  1. Confirm your exported CDR data is placed in the "exportData" folder.')
print('  2. Rename your CDR data file to "cdr.csv"\n')
print('SEARCHING INSTRUCTIONS:')
print('  Choose either a calling party (source or called party search (destination).\n')
print('  It is important NOT to include - or . characters in your number search.')
print('  For example searching for 208-625-5555... you would use 2086255555.\n')
print('  To search for more than one number, use a comma seperate list.')
print('  Example: 2086251234,2086252345,2086253456\n')
print('---------------------')

continueLookup = True
while(continueLookup):
    # Gather number(s) to search for.
    callNum = []
    uCalledOrCalling = input('\nPress 1 for calling or 2 for called:')
    uNumLookup = input('\nPlease enter the called number in the format XXXXXXXXXX:')
    callNum = uNumLookup.split(',')

    csvFile = "exportData/cdr.csv"
    csvData = pd.read_csv(csvFile, index_col = 0, low_memory=False, usecols = ['dateTimeOrigination', 'callingPartyNumber', 'originalCalledPartyNumber', 'globalCallID_callId', 'duration'])
    csvData = csvData[csvData['duration'] != 0]
    csvData = csvData.dropna()

    if uCalledOrCalling == '1':
        calllingOrCalled = 'callingPartyNumber'
    else:
        calllingOrCalled = 'originalCalledPartyNumber'

    for num in callNum:
        str(num)
        # Filter all rows for the desired search
        result = csvData[csvData[calllingOrCalled].str.contains(num, regex=True)]

        # Convert unix date time
        result['dateTimeOrigination'] = pd.to_datetime(result['dateTimeOrigination'], unit='s', origin='unix', utc=True)
        result['dateTimeOrigination'] = result['dateTimeOrigination'].dt.tz_convert('America/Los_Angeles')
        totalCallsSum = str(result.shape[0])

        # Calculate the total calls for the called number by date
        print('\n')
        print('----     CDR RESULTS     ----')
        if uCalledOrCalling == '1':
            print('The calling number ' + num + ' has made ' + totalCallsSum + ' calls.\n')
        else:
            print('The called number ' + num + ' has been called ' + totalCallsSum + ' times.\n')
        print('---- TOTAL CALLS PER-DAY ----')
        print('dateTime, totalCalls')
        datez = pd.to_datetime(result['dateTimeOrigination'], unit='s', origin='unix')
        totalCalls = datez.groupby(datez.dt.floor('d')).size().reset_index(name='count')
        for date in totalCalls.index:
            todaysDate = totalCalls['dateTimeOrigination'][date]
            todaysCount = totalCalls['count'][date]
            print(todaysDate.strftime('%Y-%m-%d') + ', ' + str(todaysCount))

        # Ask user if they would like to see each individual call
        uInput = False
        x = input('\nWould you like to see all calls? (y/n) ').lower()
        if x.startswith('y'): uInput = True

        # Sort results from oldest to newest
        result = result.sort_values(by='dateTimeOrigination')

        # Print out all individual results
        if uInput:
            print('\n----  INDIVIDUAL CALLS   ----')
            print('Timezone: America/Los_Angeles')
            print('CallID  Date/Time Orig.            Calling P.  Called P.   Dura')
            print(result.to_string(header=False, index_names=False))

    continueLookup = False
    ctLookupInput = input('\n\nWould you like to lookup another number? (y/n) ').lower()
    if ctLookupInput.startswith('y'): continueLookup = True

print('\n\nComplete...\n')