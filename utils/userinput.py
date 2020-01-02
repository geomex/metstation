'''
Description:

Run this script to ask for user input for SNOTEL Data.

by: Joel A. Gongora
date: 02/19/2018
'''

import pickle
import numpy as np
import pandas as pd
from os.path import abspath
import os
import sys
if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))
from plotting import plot_time_series

# -------------------------------------------------------- #
#           Request User Input [STATE]                     #
# -------------------------------------------------------- #


def enterstate():
    state = input("Enter the two letter abbrv. of the " +
                  "state you wish to plot: ")
    print("\n")
    return state


def selectsite():
    site = input("Enter the name of the " +
                 "site you wish to plot: ")
    print("\n")
    return site

# -------------------------------------------------------- #
#           Check for Existance of Directory               #
#           ../figures, if not create it                   #
# -------------------------------------------------------- #


def load_snotel(state):
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

    # -------------------------------------------------------- #
    #           Drop Nulls and Nans                            #
    #           Convert Each Date to datetime                  #
    # -------------------------------------------------------- #

    for llave in snotel_keys:
        snotel[llave] = snotel[llave].replace('nan', np.nan)
        try:
            snotel[llave].dropna(inplace=True)
            snotel[llave]['date'] = pd.to_datetime(
                snotel[llave]['date'],
                infer_datetime_format=True
            )
        except KeyError:
            columns = snotel[llave].columns.tolist()
            columns = [
                columns[i].strip().lower()
                .replace(' ', '_').replace('(', '')
                .replace(')', '')
                for i in np.arange(len(columns))
            ]
            snotel[llave].columns = columns
            snotel[llave].dropna(inplace=True)
            snotel[llave]['date'] = pd.to_datetime(
                snotel[llave]['date'],
                infer_datetime_format=True
            )
        except KeyError:
            print(
                'Oops, something is not quite right with Snotel Site:\n\n' +
                llave + '\n\nPlease check the pickled file for errors.\n\n'
            )
    return snotel, snotel_keys

# -------------------------------------------------------- #
#           Request User to Input [Snotel Site]            #
# -------------------------------------------------------- #


def entersite(snotel, snotel_keys):
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
    data.set_index('date', inplace=True)
    return data, snotel_keys[indices[0]]


if __name__ == "__main__":
    print('Executing as main program.')
    state = enterstate()
    snotel, snotel_keys = load_snotel(state)
    snotel = entersite(snotel, snotel_keys)
