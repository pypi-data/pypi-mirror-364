import pandas as pd
import numpy as np

def parseFileSize(sz):
    """
    Converts a bit-format integer filesize into a string of appropriate declension (kb, mb, gb) with the appropriate ending.
    """
    if sz > 1000000000:
        return '{:.2f}gb'.format(sz/1000000000)
    elif sz > 1000000:
        return '{:.1f}mb'.format(sz/1000000)
    elif sz > 1000:
        return '{:.1f}kb'.format(sz/1000)
    else:
        return str(sz)+'b'
    
def compression(f1, f2):
    """
    Yields a string percentage of filesize reduction for two bit-format integer size inputs.
    """
    f1 = int(f1)
    f2 = int(f2)
    largeFile = max(f1, f2)
    smallFile = min(f1, f2)
    return "{:.1f}%".format((1 - smallFile / largeFile) * 100)


def getColumnData(df, colname=""):
    """
    Yields a tuple of (column name, column units, full column name) for the specified name. Returns -1 if no matching column name
    If no column name is provided, returns a list with all signals in the same format.
    """

    columns = list(df.columns)
    units = []
    name = []
    fullname = []

    for column in columns:
        if "[" in column:
            units.append(column.split("[")[1].split("]")[0])
            name.append(column.split("[")[0])
            fullname.append(column)
        else:
            units.append("")
            name.append(column.split("[")[0])
            fullname.append(column)
    
    columns = name
    
    if colname != "":
        for (idx, col) in enumerate(columns):
            if col == colname:
                return (col, units[idx], fullname[idx])
        for (idx, col) in enumerate(columns):
            if col.lower() in colname.lower():
                return (col, units[idx], fullname[idx])
        return -1
    else:
        return list(zip(columns, units, fullname))

def discard(df_old, prefs, empty = True):
    """
    Discards columns based on a preferences file in .json format. 
    By default, discards columns identified as empty. 
    Returns the resultant df.
    """
    df = df_old.copy()
    to_discard = prefs['discard'].dropna()
    columns = df.columns

    # Wildcard search
    for search_item in to_discard.index:
        if "*" in search_item:
            split_location = search_item.index("*")
            start_str = search_item.split("*")[0]
            end_str = search_item.split("*")[1]
            for column in columns:
                name = column.split('[')[0].strip()
                if name[0:len(start_str)] == start_str and name[split_location:(split_location+len(end_str))] == end_str:
                    df = df.drop(column, axis=1)

    columns = df.columns
    # Traditional search
    for column in columns:
        name = column.split('[')[0].strip()
        if name in to_discard.index:
            df = df.drop(column, axis=1)
        elif (df[column] == 0).all() and empty:
            df = df.drop(column, axis=1)
        elif "Unnamed" in column:
            df = df.drop(column, axis=1)
    
    return df

def squish(df, prefs):
    """
    Preforms data trimming on a dataframe based on passed preferences in a .json format.
    Returns reduced size dataframe
    """
    
    # Reformat time column to save decimals
    df["t[s]"] = df["t[s]"].astype(int)

    # Units and Names
    units = prefs['units'].dropna()
    names = prefs['names'].dropna()

    # Identify column types
    columns = df.columns
    for column in columns:
        try:
            tag = column.split('[')[1].split(']')[0]
        except:
            tag = ""
        name = column.split('[')[0].strip()
        if name in names.index:
            df[column] = df[column].astype(float).round(int((names[name])))
        elif tag.lower() in units.index:
            df[column] = df[column].astype(float).round(int((units[tag.lower()])))
    return df

def id_patch(keep):
    """
    Identifies patches in the form of tuples of indices.
    Rising/falling edge for boolean list in the form of a 1D DF.
    """

    # Cast DF to list and init empty lists for start/finish indices
    keep = keep.values.tolist()
    start = []
    finish = []

    # Loop through each element and find high/low changes
    for i, k in enumerate(keep):
        if i > 0 and keep[i] != keep[i-1]:
            if len(start) <= len(finish):
                start.append(i)
            else:
                finish.append(i)
        elif i == 0 and not keep[i]:
            start.append(i)

    # Zip into tuples, then list and return
    result = list(zip(start, finish))
    return result

def interp(df, indices):
    """
    Interpolates data in a provided df based on index sets to replace. 
    """
    for index in indices:
        if index[0] != 0:
            for i in range(index[0], index[1]):
                df.iloc[i] = (df.iloc[index[0]-1] + (i-index[0]+1)*(df.iloc[index[1]] - df.iloc[index[0]-1])/len(range(index[0], index[1]+1)))
        else:
            for i in range(index[0], index[1]):
                df.iloc[i] = df.iloc[index[1]]
    return df

def gps_filter_data(df):
    """
    Yields a GPS-refined copy of the input dataframe. Does no other cleaning.
    Previously make use of GCD algorithm. Now makes use of the FCC distance formula.
    https://en.wikipedia.org/wiki/Geographical_distance#FCC's_formula
    """
    new_df = df.copy()

    # Calculate distances traveled
    x = np.radians(new_df['GPS_x[°]'])
    y = np.radians(new_df['GPS_y[°]'])
    dx = np.append(x.diff().iloc[1:-1], 0)
    dy = np.append(y.diff().iloc[1:-1], 0)
    x_m = (x[0:-2] + x[1:-1]) / 2
    
    K1 = 111.13209 - 0.56605 * np.cos(2 * np.radians(x_m)) + 0.0012 * np.cos(4 * np.radians(x_m))
    K2 = 111.41513 * np.cos(np.radians(x_m)) - 0.09455 * np.cos(3 * np.radians(x_m)) + 0.00012 * np.cos(5 * np.radians(x_m))
    dist = np.sqrt(np.square(K1 * dx) + np.square(K2 * dy)) * 1000

    keep_dist = dist < 1000

    # Keep distance under 1km or geofenced into the US
    lat_left, lon_bottom, lat_right, lon_top = [-170, 25, -65, 70]
    keep_region = (new_df['GPS_x[°]'].iloc[0:-1] < lat_right) & (new_df['GPS_x[°]'].iloc[0:-1] > lat_left) & (new_df['GPS_y[°]'].iloc[0:-1] > lon_bottom) & (new_df['GPS_y[°]'].iloc[0:-1] < lon_top)
    keep = keep_dist & keep_region
    for idx in [0, len(df)-1, len(df)-2]: 
        keep[idx] = True
    
    new_df['GPS Replaced [STATE]'] = ~keep
    patches = id_patch(keep)
    for signal in ['GPS_x[°]', 'GPS_y[°]', 'GPS_z[m]', 'GPS_speed[kph]', 'GPS_speed_mph[mph]', 'GPS_speed_mph[]']:
        new_df.loc[:, signal] = interp(df.loc[:, signal], patches)
    
    # Recalculate Distance for total traveled (odometer)
    x = np.radians(new_df['GPS_x[°]'])
    y = np.radians(new_df['GPS_y[°]'])
    dx = np.append(x.diff().iloc[1:-1], 0)
    dy = np.append(y.diff().iloc[1:-1], 0)
    x_m = (x[0:-2] + x[1:-1]) / 2
    #print("dx {} dy {} x_m {}".format(len(dx), len(dy), len(x_m)))
    
    K1 = 111.13209 - 0.56605 * np.cos(2 * np.radians(x_m)) + 0.0012 * np.cos(4 * np.radians(x_m))
    K2 = 111.41513 * np.cos(np.radians(x_m)) - 0.09455 * np.cos(3 * np.radians(x_m)) + 0.00012 * np.cos(5 * np.radians(x_m))

    #print(K1)
    #print(K2)

    dist = list(np.sqrt(np.square(K1 * dx) + np.square(K2 * dy)) * 1000)

    dist_traveled = [0]
    for i in range(1, len(dist)):
        dist_traveled.append(round(2*(dist_traveled[i-1]+dist[i]), 0)/2)
        # print(" {} Add ".format(i)+str(sum(dist[0:(i-1)])))
    dist_traveled[-1] = dist_traveled[len(df)-3]
    dist_traveled.append(dist_traveled[len(df)-3])
    
    
    # Pre-round and save
    dist_traveled = pd.Series(dist_traveled)
    dist_traveled.name = 'GPS_Distance_Traveled[m]'
    new_df["Cumulative Distance [m]"] = dist_traveled

    return new_df

def comparativeDF(df, signalA, signalB, asList = True, name = ""):
    """
    Outputs the signalA name -> signalB name difference (A > B, relative is positive)
    """
    signalA_name = getColumnData(df, signalA)[2]
    signalB_name = getColumnData(df, signalB)[2]

    result = df[signalA_name] - df[signalB_name]
    result.name = name

    if not asList and name == "":
        raise ValueError("Name must be defined if result is passed as DF (asList = False).")

    if asList:
        return result.values.tolist()
    else:
        return result

def roundCols(df, rounding_accuracy):
    """
    Given a dataframe and a rounding accuracy dict, returns the dataframe with each column rounded to spec.
    """
    new_df = df.copy()

    for column in new_df.columns:
        new_df[column] = new_df[column].astype(float).round(rounding_accuracy[column])

    return new_df

def parseName(columns, key):
    """
    Given columns in the form of df.columns, yields the full column name matching the abbreviated key input
    E.g. for columns ['Col1[C]', 'Col2[F]', 'Col3[K]'] and key 'col2', 'Col2[F]' would be returned.
    If no match, returns -1
    """
    for column in columns:
        if key.lower().strip() == column.split('[')[0].lower().strip():
            return column
    return -1

def signalFromName(df, name):
    """
    Yields all the associated data with a specific abbreviated name input.
    If no match, returns a list of the appropriate size of 0s
    """
    if parseName(df.columns, name) != -1:
        return list(df[parseName(list(df.columns), name)])
    else:
        return [0]*len(df)

def formatData(df, signal_x, signals_y=""):
    """
    Given a DF object and a signal name, returns a list of the raw data under that column.
    If provided a second signal, either as a name or a list of names, returns an N dimensional array.
    """
    if signals_y == "":
        return signalFromName(df, signal_x)
    elif type(signals_y) != list:
        signals_y = [signals_y]
    res = [signalFromName(df, signal_x)]
    for signal in signals_y:
        res.append(signalFromName(df, signal))
    return res

def ema(data, span=3):
    """
    Standard Exponential Moving Average Filter
    Given a list input and a span input, outputs a list of the same length with the filter applied.
    Original implementation by Dayanand Shah.
    """
    alpha = 2 / (span + 1)
    ema_values = []
    
    # Initialize the first EMA with the first data point
    if data:
        ema_values.append(data[0])
    
    # Calculate subsequent EMAs
    for i in range(1, len(data)):
        ema_values.append((data[i] * alpha) + (ema_values[-1] * (1 - alpha)))
        
    return ema_values

def applyFilter(data, toFilter=[], span=3):
    """
    Provided a list of numbers or a list of lists of numbers, applies an EMA filter to relevant data and returns the result.
    """
    if data:
        if isinstance(data[0], list):
            res = []
            
            for (i,col) in enumerate(data):
                if toFilter == [] or i in toFilter:
                    res.append(ema(col, span))
                else:
                    res.append(col)
            return res
        else:
            return ema(data, span)
