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
    uCalledOrCalling = input('\nPress 1 for calling or 2 for called: ')
    uDurationZero = input('Include calls with duration zero? (y/n) ').lower()
    uNumLookup = input('Please enter the called number in the format XXXXXXXXXX: ')
    callNum = uNumLookup.split(',')

    # Import CDR data and filter specific columns, strip any columns with NaN
    csvFile = "exportData/cdr.csv"
    csvData = pd.read_csv(csvFile, index_col = 0, low_memory=False, usecols = ['dateTimeOrigination', 'callingPartyNumber', 'originalCalledPartyNumber', 'globalCallID_callId', 'duration'])
    csvData = csvData.dropna()
    # Filter search based on user choice
    if uDurationZero == 'n': csvData = csvData[csvData['duration'] != 0]

    # Filter search based on user choice
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

        print(result.to_string(header=False, index_names=False))

    continueLookup = False
    ctLookupInput = input('Would you like to lookup another number? (y/n) ').lower()
    if ctLookupInput.startswith('y'): continueLookup = True

print('\nComplete...\n')