import pandas as pd
# from datetime import datetime, date
import datetime
from gsheet_reader import get_cg_data



def get_youths(CG):
    """Return a list of youths in each cg"""
    df = get_cg_data(CG)
    return df['Name (as in NOAH)'].tolist()




def get_latest_dates():
    """Returns the 4 latest dates that has an event on it"""
    dates = SA_C.columns.to_list()[5:]
    dates = [date.split('\n')[0] if (len(date.split()[0]) == 2) else "0{}".format(date.split('\n')[0]) for date in
             dates]
    dates = [datetime.datetime.strptime(date, '%d %b %Y') for date in dates]
    nearest = min(dates, key=lambda x: abs(x - datetime.datetime.today()))
    idx = dates.index(nearest)
    output = dates[idx - 4:idx]
    output = [datetime.datetime.strftime(date, '%d %b %Y') for date in output]
    return output


if __name__ == '__main__':
    # print(get_latest_dates())
    # print(date.today())
    print(get_youths('SA A'))
