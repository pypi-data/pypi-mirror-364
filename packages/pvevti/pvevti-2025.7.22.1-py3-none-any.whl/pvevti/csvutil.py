import os
import pandas as pd

def read_csv(filepath):
    return pd.read_csv(filepath, encoding='latin-1')

def write_csv(df, filepath):
    df.to_csv('temp.csv', index=False)
    return 1

def most_recent_csv(directory, ignore=""):
    """
    Yields the complete path of the most recently modified CSV in the provided directory.
    Returns -1 if no CSVs exist.
    """
    files = os.listdir(directory)
    csv_files = [directory + file for file in files if ".csv" in file and ignore not in file]
    csv_files.sort(key=os.path.getmtime)
    if len(csv_files) >= 1:
        return csv_files[-1]
    else:
        return -1

def all_csvs(directory):
    """
    Yields a list of complete paths to CSV files located in the provided directory.
    Returns -1 if no CSVs exist.
    """
    files = os.listdir(directory)
    csv_files = [directory + file for file in files if ".csv" in file]
    if len(csv_files) >= 1:
        return csv_files
    else:
        return -1

def df_from_csv(csv_name, column_names=[]):
    """
    Yields a dataframe from a provided CSV (path). 
    Only passes specified column names unless none are specified, then passes the full table.
    """
    if type(column_names) == str:
        column_names = [column_names]

    if len(column_names) > 0:
        df = pd.read_csv(csv_name, usecols=column_names, encoding="latin-1")
    else:
        df = pd.read_csv(csv_name, encoding="latin-1")
    df.drop(df.columns[df.columns.str.contains('Unnamed', case=False)], axis=1, inplace=True)
    
    return df

def df_to_csv(df, csv_name, save_index=False, addition='_Filtered'):
    """
    Saves a provided pandas df to the provided csv path.
    Returns -1 if an error occurs in saving.
        df: dataframe object to save
        csv_name: full path of CSV
        save_index (optional): defaults to false, specifies saving the index columns.
        addition (optional): defaults to "_Filtered", specifies an appendage to add to the end of the literal CSV filename
    """
    csv_name = csv_name.split('.')[0] + addition + '.csv'
    try:
        df.to_csv(csv_name, index=save_index, encoding="latin-1")
    except Exception as e:
        if e.errno == 13:
            print("[Error 13] Failed to save CSV. Make sure the file destination is not open in another application.")
        else:
            print("[Error {e.errno}] Failed to save CSV.")
        return -1
    print("Saved DF to "+csv_name)
