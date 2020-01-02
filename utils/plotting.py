'''
Tools for time series analysis

by: Joel A. Gongora
date: 02/19/2019

'''
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from os.path import abspath
import os

figs_dir = abspath('../figures/')
if not os.path.exists(figs_dir):
    os.makedirs(figs_dir)


def plot_time_series(data,
                     date_range,
                     col1,
                     col2,
                     ylabel1,
                     ylabel2,
                     state,
                     site):
    '''
    data - (pandas dataframe) with timeseries data with 'Date' as
           one of the columns.
    
    date_range - (tuple of strings) range of dates to plot and analyze
           (min_date, max_date), e.g. ('01/01/2018', '01/01/2019')
    
    col1 - (string) column name in dataframe for y-axis 1
    col2 - (string) column name in dataframe for y-axis 2
    ylabel1 - (string) Y-axis 1 Label
    ylabel2 - (string) Y-axis 2 Label
    state - (string) two letter abbrv. of the state.
    '''
    
    # ---------- Subset Data -------------------- #
    
    plt.style.use(abspath('../plotstyles/fancy_nolatex_largefont.mplstyle'))
    sub_data = data[(data['date'] > date_range[0]) &
                    (data['date'] < date_range[1])].reset_index()
    
    # ---------- Convert to Numeric Values ---------- #
    
    sub_data = sub_data.convert_objects(convert_numeric=True)
    
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
    plt.title('Time Series [SWE] \n State: {}, Site: {}'.format(
        state.upper(), site))
    plt.savefig(figs_dir + '/' + state.upper() +
                '_' + site + '_timeseries.png')
    plt.show()
    return sub_data

