import pandas as pd
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
    print('\nChoose one of the following options to search CDR records: ')
    print('1. Calling number')
    print('2. Called number')
    print('3. Originating IP address')
    print('4. Destination IP address')
    uCalledOrCalling = input('\nSelect choice: ')
    uDurationZero = input('Include calls with duration zero? (y/n) ').lower()
    uNumLookup = input('Search criteria: ')
    callNum = uNumLookup.split(',')

    # Import CDR data and filter specific columns, strip any columns with NaN
    csvFile = "exportData/cdr.csv"
    csvData = pd.read_csv(csvFile, index_col = 0, low_memory=False, usecols = ['dateTimeOrigination', 'originalCalledPartyNumber', 'globalCallID_callId', 'duration', 'origIpv4v6Addr', 'destIpv4v6Addr'])
    csvData = csvData.dropna()
    # Filter search based on user choice
    if uDurationZero == 'n': csvData = csvData[csvData['duration'] != 0]

    # Filter search based on user choice
    if uCalledOrCalling == '1':
        calllingOrCalled = 'callingPartyNumber'
    elif uCalledOrCalling == '2':
        calllingOrCalled = 'originalCalledPartyNumber'
    elif uCalledOrCalling == '3':
        calllingOrCalled = 'origIpv4v6Addr'
    elif uCalledOrCalling == '4':
        calllingOrCalled = 'destIpv4v6Addr'
    else:
        print('Invalid selection')

    print(uCalledOrCalling)

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
        elif uCalledOrCalling == '2':
            print('The called number ' + num + ' has been called ' + totalCallsSum + ' times.\n')
        elif uCalledOrCalling == '3':
            print('The source IP address ' + num + ' has made ' + totalCallsSum + ' calls.\n')
        elif uCalledOrCalling == '4':
            print('The destination IP address ' + num + ' has been utilizied ' + totalCallsSum + ' times.\n')
        else:
            print('Please try again, invalid selection.')

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
    ctLookupInput = input('Would you like to lookup another number? (y/n) ').lower()
    if ctLookupInput.startswith('y'): continueLookup = True

print('\nComplete...\n')