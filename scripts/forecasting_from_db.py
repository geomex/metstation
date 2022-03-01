# '''Description:
# Forcasting models for time series analysis.
# by: Joel A. Gongora
# date: 12/30/2019
# '''

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from os.path import abspath
import warnings
import statsmodels.api as sm
import sys
from pylab import rcParams
from fbprophet import Prophet
import os
import psycopg2
if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))

from userinput import load_snotel
from myconfig import db_config
from sqlalchemy import create_engine, types
engine = create_engine(
    'postgresql+psycopg2://joel.gongora:@localhost:5432/metstation'
)

warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')


def swe_prophet(
        swe_for_prophet=None,
        interval_width=0.95
):
    # uncertainty interval to 95% #
    swe_model = Prophet(interval_width=0.95)

    # Fit Model #
    swe_model.fit(swe_for_prophet)

    return swe_model



# ------------------------------------------------- #
# Load Dictionary of Snotels for the State of Idaho #
# ------------------------------------------------- #

states = os.listdir('../data')

snotelID_to_name = {}


for state in states:
    if len(state) == 2 and state == 'WA':
        print(f'Working on State {state}')
        datos, snotel_id = load_snotel(state)
        # ----------------------------------- #
        # Create a Table for Each Snotel Site #
        # ----------------------------------- #
        for sno_id in snotel_id:

            datos[sno_id] = datos[sno_id].replace(
                to_replace="nan", value=np.nan
            )
            # Convert to Datetime
            datos[sno_id]['date'] = pd.to_datetime(
                datos[sno_id]['date'], format="%m/%d/%y"
            )

            # ------------------ #
            # Convert to Numeric #
            # ------------------ #                

            for col in datos[sno_id].columns:
                if col not in ['date', 'site_name', 'state', 'site_id']:
                    datos[sno_id][col] = pd.to_numeric(datos[sno_id][col])
                    if col in ['site_id']:
                        datos[sno_id][col] = datos[sno_id][col].astype('int')
                    else:
                        datos[sno_id][col] = datos[sno_id][col].astype('str')
            datos[sno_id] = datos[sno_id].replace(
                to_replace="nan", value=np.nan
            )
            site_name = sno_id.split(':')[1].split(',')[0].strip()
            columns = datos[sno_id].columns.tolist()
            columns = [
                columns[i].strip().lower()
                .replace(' ', '_').replace('(', '')
                .replace(')', '')
                for i in np.arange(len(columns))
            ]
            datos[sno_id].columns = columns
            # Rename 
            tmp = datos[sno_id][
                ['date','snow_water_equivalent_in_start_of_day_values']
            ].rename(
                columns={
                    'date':'ds',
                    'snow_water_equivalent_in_start_of_day_values':'y'
                }
            )
            number_of_nonnans = tmp.loc[~tmp['y'].isna(), :].shape[0]
            
            if number_of_nonnans < 10:
                continue
            # Use fbprophet to predict SWE #
            else:
                swe_model = swe_prophet(
                    swe_for_prophet=tmp,
                    interval_width=0.95
                )
                test = swe_model.make_future_dataframe(periods=100)
                f = swe_model.predict(test)
                datos[sno_id] = pd.concat([datos[sno_id], f], axis=1)
                # ----------------------------- #
                # Add Site Name and ID to Table #
                # ----------------------------- # 
                datos[sno_id]['site_name'] = site_name
                datos[sno_id]['site_id'] = sno_id.split(':')[0].split(" ")[1]
                # ----------------------- #
                # Add State Name to TAble #
                # ----------------------- #
                datos[sno_id]['state'] = state
                # Push DataFrame to DB #
                datos[sno_id][
                    [
                        'date',
                        'site_id',
                        'site_name',
                        'state',
                        'trend',
                        'yhat',
                        'yhat_lower',
                        'yhat_upper',
                        'trend_lower',
                        'trend_upper',
                        'additive_terms',
                        'additive_terms_lower',
                        'additive_terms_upper',
                        'weekly',
                        'weekly_lower',
                        'weekly_upper',
                        'yearly',
                        'yearly_lower',
                        'yearly_upper',
                        'multiplicative_terms',
                        'multiplicative_terms_lower',
                        'multiplicative_terms_upper'
                    ]
                ].to_sql(
                    'snotel_fbprophet',
                    engine,
                    if_exists='append',
                    index=False,
                    dtype={
                        'date': types.DATE,
                        'site_id': types.INTEGER,
                        'site_name': types.VARCHAR(50),
                        'state': types.VARCHAR(3),
                        'trend': types.REAL,
                        'yhat': types.REAL,
                        'yhat_lower': types.REAL,
                        'yhat_upper': types.REAL,
                        'trend_lower': types.REAL,
                        'trend_upper': types.REAL,
                        'additive_terms': types.REAL,
                        'additive_terms_lower': types.REAL,
                        'additive_terms_upper': types.REAL,
                        'weekly': types.REAL,
                        'weekly_lower': types.REAL,
                        'weekly_upper': types.REAL,
                        'yearly': types.REAL,
                        'yearly_lower': types.REAL,
                        'yearly_upper': types.REAL,
                        'multiplicative_terms': types.REAL,
                        'multiplicative_terms_lower': types.REAL,
                        'multiplicative_terms_upper': types.REAL
                    }
                )

