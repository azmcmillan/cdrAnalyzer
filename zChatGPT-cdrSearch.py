import pandas as pd
from datetime import datetime, timezone, timedelta

# Set pandas display options
pd.set_option('display.max_rows', None)  # Set to None to display all rows, or choose a large number

def convert_unix_to_pst(unix_time):
    """
    Converts Unix time to PST (Pacific Standard Time).
    :param unix_time: The Unix time in seconds.
    :return: A datetime object in PST.
    """
    # Convert Unix time to UTC
    utc_time = datetime.utcfromtimestamp(int(unix_time)).replace(tzinfo=timezone.utc)

    # Convert UTC to PST (UTC-8 hours)
    pst_time = utc_time.astimezone(timezone(timedelta(hours=-8)))

    return pst_time.strftime('%Y-%m-%d %H:%M:%S')

def read_cdr_data(file_path):
    """
    Reads specific columns of the CDR data from a CSV file.
    :param file_path: The path to the CSV file.
    :return: A pandas DataFrame containing the specified CDR data.
    """
    columns = ['dateTimeOrigination', 'callingPartyNumber', 'originalCalledPartyNumber', 'globalCallID_callId', 'duration']
    return pd.read_csv(file_path, usecols=columns, engine='python')

def search_cdr_data(df, number, is_calling_party, exclude_zero_duration=False):
    """
    Searches the CDR data for a specific calling or called party number and returns only selected columns.
    :param df: The DataFrame containing the CDR data.
    :param number: The calling or original called party number to search for.
    :param is_calling_party: Boolean indicating if the number is a calling party number.
    :param exclude_zero_duration: Exclude calls with zero duration if True.
    :return: A DataFrame with the search results.
    """
    columns_to_display = ['globalCallID_callId', 'dateTimeOrigination', 'callingPartyNumber',
                          'originalCalledPartyNumber', 'duration']

    if is_calling_party:
        df = df[df['callingPartyNumber'] == number]
    else:
        df = df[df['originalCalledPartyNumber'] == number]

    if exclude_zero_duration:
        df = df[df['duration'] != 0]

    df['dateTimeOrigination'] = df['dateTimeOrigination'].apply(convert_unix_to_pst)
    df['date'] = pd.to_datetime(df['dateTimeOrigination']).dt.date

    calls_per_day = df.groupby('date').size()
    return df[columns_to_display], calls_per_day

def main():
    file_path = input("Enter the path of the CDR CSV file: ")
    cdr_data = read_cdr_data(file_path)

    while True:
        search_option = input("\nSearch by (1) Calling Party Number, (2) Original Called Party Number, or 'exit' to quit: ")

        if search_option.lower() == 'exit':
            print("Exiting the program.")
            break

        numbers_input = input("Enter the numbers (comma-separated): ")
        numbers_list = [num.strip() for num in numbers_input.split(',')]

        exclude_zero_duration = input("Exclude calls with zero duration? (yes/no): ").lower() == 'yes'
        is_calling_party = search_option == '1'
        show_summary = input("Show summary of calls per day? (yes/no): ").lower() == 'yes'

        for number in numbers_list:
            print(f"\nResults for number: {number}")
            results, calls_per_day = search_cdr_data(cdr_data, number, is_calling_party, exclude_zero_duration)

            if results.empty:
                print("No records found for number:", number)
            else:
                print("Individual Call Details for number", number, ":")
                print(results)
                if show_summary:
                    print("\nSummary of Calls per Day for number", number, ":")
                    print(calls_per_day)

if __name__ == "__main__":
    main()
