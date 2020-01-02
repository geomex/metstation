'''Description:

This script will ask the user for some input and then produce
some forecasting results, along with figures demonstrating the
models ability to forecast.

by: Joel A. Gongora
date: Feb. 22 2019
'''

import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from os.path import abspath
import os
import itertools
import warnings
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
import statsmodels.api as sm
import sys
if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))

#######################################
# Import Tool to Extract Scraped Data #
#######################################

import userinput

state = userinput.enterstate()
snotel, snotel_keys = userinput.load_snotel(state)
site, site_name =  userinput.entersite(snotel, snotel_keys)
