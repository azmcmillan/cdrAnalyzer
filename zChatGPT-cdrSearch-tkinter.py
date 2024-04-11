import pandas as pd
from datetime import datetime, timezone, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox

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

class CDRSearchApp:
    def __init__(self, master):
        self.master = master
        master.title("CDR Search App")

        self.file_path_label = tk.Label(master, text="Enter the path of the CDR CSV file:")
        self.file_path_label.pack()

        self.file_path_entry = tk.Entry(master)
        self.file_path_entry.pack()

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        self.search_option_var = tk.StringVar(value="calling")
        self.calling_radio = tk.Radiobutton(master, text="Calling Party", variable=self.search_option_var, value="calling")
        self.calling_radio.pack()

        self.called_radio = tk.Radiobutton(master, text="Called Party", variable=self.search_option_var, value="called")
        self.called_radio.pack()

        self.numbers_label = tk.Label(master, text="Enter the numbers (comma-separated):")
        self.numbers_label.pack()

        self.numbers_entry = tk.Entry(master)
        self.numbers_entry.pack()

        self.exclude_zero_duration_label = tk.Label(master, text="Exclude calls with zero duration? (yes/no):")
        self.exclude_zero_duration_label.pack()

        self.exclude_zero_duration_entry = tk.Entry(master)
        self.exclude_zero_duration_entry.pack()

        self.show_summary_label = tk.Label(master, text="Show summary of calls per day? (yes/no):")
        self.show_summary_label.pack()

        self.show_summary_entry = tk.Entry(master)
        self.show_summary_entry.pack()

        self.search_button = tk.Button(master, text="Search", command=self.search_cdr)
        self.search_button.pack()

        self.exit_button = tk.Button(master, text="Exit", command=self.exit_program)
        self.exit_button.pack()

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def search_cdr(self):
        file_path = self.file_path_entry.get()
        cdr_data = read_cdr_data(file_path)

        search_option = self.search_option_var.get()
        numbers_input = self.numbers_entry.get()
        numbers_list = [num.strip() for num in numbers_input.split(',')]

        exclude_zero_duration = self.exclude_zero_duration_entry.get().lower() == 'yes'
        show_summary = self.show_summary_entry.get().lower() == 'yes'

        for number in numbers_list:
            results, calls_per_day = search_cdr_data(cdr_data, number, search_option == 'calling', exclude_zero_duration)

            if results.empty:
                messagebox.showinfo("No Records Found", f"No records found for number: {number}")
            else:
                messagebox.showinfo(f"Results for number: {number}", f"Individual Call Details for number {number}:\n{results}")
                if show_summary:
                    messagebox.showinfo(f"Summary for number: {number}", f"Summary of Calls per Day:\n{calls_per_day}")

    def exit_program(self):
        self.master.destroy()

def main():
    root = tk.Tk()
    app = CDRSearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()