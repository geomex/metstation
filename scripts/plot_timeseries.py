'''This script will plot the time series of the State entered by the
user as well as the Snotel Site (if specified)

by: Joel A. Gongora
date: Jan. 23, 2019

'''

import pickle
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter
from os.path import abspath
import os


# -------------------------------------------------------- #
#           Request User Input [STATE]                     #
# -------------------------------------------------------- #

state = input("Enter the two letter abbrv. of the " +
              "state you wish to plot: ")

print("\n")

# -------------------------------------------------------- #
#           Check for Existance of Directory               #
#           ../figures, if not create it                   #
# -------------------------------------------------------- #

figs_dir = abspath('../figures/')
if not os.path.exists(figs_dir):
    os.makedirs(figs_dir)

# ----------------------------------------- #
#            Load SNOTEL DATA               #
# ----------------------------------------- #

carpeta = abspath('../data/' + state.upper() + '/')
print(carpeta)

with open(carpeta + '/' + 'allsnotel_dict.pickle', 'rb') as f:
    snotel = pickle.load(f)

with open(carpeta + '/' + 'keys.pickle', 'rb') as f:
    snotel_keys = pickle.load(f)


# ------------------------------------------------------- #
#           Request User to Input [Snotel Site]            #
# -------------------------------------------------------- #


print(("\n".join(list(snotel_keys))))
site = input("\n Enter the SNOTEL site ID number you wish to plot" +
             "(from list above) \n if you'd like to plot all" +
             "enter 'ALL': \n")

# -------------------------------------------------------- #
#                     Data Selection                       #
# -------------------------------------------------------- #


if site == 'ALL':
    print('Will plot all')
else:
    indices = [i for i, s in enumerate(snotel_keys) if site in s]
    data = snotel[snotel_keys[indices[0]]]

data = data.dropna()
data['date'] = pd.to_datetime(data['date'])

# -------------------------------------------------------- #
#                Define Plotting Function                  #
# -------------------------------------------------------- #


def plot_time_series(data,
                     date_range,
                     col1,
                     col2,
                     ylabel1,
                     ylabel2):
    '''
    data - (pandas dataframe) with timeseries data with 'Date' as
           one of the columns.

    date_range - (tuple of strings) range of dates to plot and analyze
           (min_date, max_date), e.g. ('01/01/2018', '01/01/2019')

    col1 - (string) column name in dataframe for y-axis 1
    col2 - (string) column name in dataframe for y-axis 2
    ylabel1 - (string) Y-axis 1 Label
    ylabel2 - (string) Y-axis 2 Label
    '''

    # ---------- Subset Data -------------------- #

    plt.style.use('../plotstyles/fancy_nolatex_largefont.mplstyle')
    sub_data = data[(data['date'] > date_range[0]) &
                    (data['date'] < date_range[1])].reset_index()

    # ---------- Convert to Numeric Values ---------- #

    sub_data = sub_data._convert(numeric=True)

    # ---------- Plot Column 1 ---------- #

    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_subplot(111)
    ax1.plot(sub_data['date'].values,
             sub_data[col1].values)
    ax1.set_ylabel(ylabel1)

    # ---------- Plot Column 2 ---------- #

    ax2 = ax1.twinx()
    ax2.plot(sub_data['date'].values,
             sub_data[col2].values, 'r-')
    ax2.set_ylabel(ylabel2, color='r')
    for t1 in ax2.get_yticklabels():
        t1.set_color('r')

    # ---------- Date Formatter ---------- #
    myFmt = DateFormatter("%m/%d")
    ax1.xaxis.set_major_formatter(myFmt)

    # ---------- Rotate Axis ---------- #

    ax1.xaxis.set_tick_params(rotation=70)
    plt.subplots_adjust(bottom=0.15)
    plt.title(
        'Time Series [SWE] \n State:{}, Site:{}'.format(
            state.upper(), site)
    )
    plt.savefig(figs_dir + '/' + state.upper() +
                '_' + site + '_timeseries.png')
    plt.show()
    return sub_data


data.columns = (
    data.columns.str.strip()
    .str.lower().str.replace(' ', '_')
    .str.replace('(', '').str.replace(')', '')
)

data.dropna()

# -------------------------------------------------------- #
#           Request User to Input Date Range               #
# -------------------------------------------------------- #

date_range = input("\nEnter the Range of Dates (MM/DD/YYY) wish \n "
                   "to plot separated by a commma \n  " +
                   "(e.g. 01/01/2018, 02/02/2019): \n ")

# ----------- Reformat for Date Range ---------- #

date_range = tuple([pd.to_datetime(txt.strip())
                    for txt in date_range.split(',')])

for count, val in enumerate(list(data.columns)):
    if count != 0:
        print(count, val)

col1 = 'snow_water_equivalent_in_start_of_day_values'
col2 = 'air_temperature_maximum_degf'
ylabel1 = 'SWE [in]'
# ylabel2 = 'Max Air Temp [deg F]'
ylabel2 = 'Min Air Temp [deg F]'
sub_data = plot_time_series(data,
                            date_range,
                            col1,
                            col2,
                            ylabel1,
                            ylabel2)
