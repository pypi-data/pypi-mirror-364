import pandas as pd
import os

class Prefs():
    def getPrefs(path=""):
        if path == "":
            pref_path = os.path.dirname(os.path.abspath(__file__))+'\\prefs.json'
        elif "prefs.json" not in path:
            pref_path = path+'\\prefs.json'
        else:
            pref_path = path
        return pd.read_json(pref_path)

    def extractUnits(prefs):
        return list(zip(prefs['units'].dropna().index.tolist(), prefs['units'].dropna().astype(int).tolist()))
    
    def extractNames(prefs):
        return list(zip(prefs['names'].dropna().index.tolist(), prefs['names'].dropna().astype(int).tolist()))

    def extractDiscard(prefs):
        return prefs['discard'].dropna().index.tolist()

    def columnsToDrop(columns, prefs):
        """
        Columns must be input as a columns item (i.e. columnds = df.columns)
        Prefs must be a pd prefs object, created with Prefs.getPrefs()
        Returns a list of column names from the original df to drop
        """
        to_discard = Prefs.extractDiscard(prefs)
        result = []

        # Wildcard search
        for search_item in to_discard:
            if "*" in search_item:
                split_location = search_item.index("*")
                start_str = search_item.split("*")[0]
                end_str = search_item.split("*")[1]
                for column in columns:
                    name = column.split('[')[0].strip()
                    if name[0:len(start_str)] == start_str and name[split_location:(split_location+len(end_str))] == end_str:
                        result.append(column)
        
        # Trad search
        for column in columns:
            if column.split("[")[0].strip() in to_discard or "Unnamed" in column:
                result.append(column)

        return result

    def getRoundingAcc(prefs, columns):
        """
        Columns must be input as a columns item (i.e. columnds = df.columns)
        Prefs must be a pd prefs object, created with Prefs.getPrefs()
        Returns a dict of keys and values for rounding accuracy.
        """
        
        byUnits = Prefs.extractUnits(prefs)
        byName  = Prefs.extractNames(prefs)
        colResult = {}

        for column in columns:
            colName = column.split("[")[0]
            colUnit = column.split("[")[1].split("]")[0]
            for (name, acc) in byName:
                if colName == name:
                    colResult[column] = acc

            if column not in colResult:
                for (unit, acc) in byUnits:
                    if colUnit.lower() == unit.lower():
                        colResult[column] = acc
            
            if column not in colResult:
                colResult[column] = 0
        
        return colResult

prefs = Prefs.getPrefs(r"C:\Users\AIBENJA\Downloads\Distance.py Active Development\prefs.json")
data = pd.read_csv(r"C:\Users\AIBENJA\Downloads\Erroneous Data 2.csv", encoding="latin-1")

# print(Prefs.extractDiscard(prefs))
toDrop = Prefs.columnsToDrop(data.columns, prefs)
roundAcc = Prefs.getRoundingAcc(prefs, data.columns)