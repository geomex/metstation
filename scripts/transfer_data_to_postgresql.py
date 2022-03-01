'''Description: This script will move the data from the pickled
format/directory into postgresql

by: Joel A. Gongora
date: 12/25/2019
'''
from os.path import abspath
import os
import sys
import numpy as np
from sqlalchemy import create_engine, types
import pandas as pd

if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))

from userinput import load_snotel
# from myconfig import db_config

engine = create_engine(
    'postgresql+psycopg2://joel.gongora:@localhost:5432/metstation'
)

# ------------------------------------------------- #
# Load Dictionary of Snotels for the State of Idaho #
# ------------------------------------------------- #

states = os.listdir('../data')
print(states)

snotelID_to_name = {}

for state in states:
    print(f'Working on State {state}')
    datos, snotel_id = load_snotel(state)
    # ----------------------------------- #
    # Create a Table for Each Snotel Site #
    # ----------------------------------- #
    for sno_id in snotel_id:
        print(sno_id)
        datos[sno_id] = datos[sno_id].replace(
            to_replace="nan", value=np.nan
        )
        # Convert to Datetime
        datos[sno_id]['date'] = pd.to_datetime(
            datos[sno_id]['date'], format="%m/%d/%y"
        )
        # Convert to Numeric
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

        # Define Table Name to Be Snotel ID #
        datos[sno_id]['site_id'] = sno_id.split(':')[0].split(" ")[1]

        # Add Site Name to TAble #
        site_name = sno_id.split(':')[1].split(',')[0].strip()


        datos[sno_id]['site_name'] = site_name
        # Add State Name to TAble #
        datos[sno_id]['state'] = state
        columns = datos[sno_id].columns.tolist()
        columns = [
            columns[i].strip().lower()
            .replace(' ', '_').replace('(', '')
            .replace(')', '')
            for i in np.arange(len(columns))
        ]
        datos[sno_id].columns = columns


        # Pus DataFrame to DB #
        datos[sno_id].to_sql(
            'snotel',
            engine,
            if_exists='append',
            index=False,
            dtype={
                'date': types.DATE,
                'snow_water_equivalent_in_start_of_day_values': types.REAL,
                'precipitation_accumulation_in_start_of_day_values': types.REAL,
                'air_temperature_maximum_deg': types.REAL,
                'air_temperature_minimum_degf': types.REAL,
                'air_temperature_average_degf': types.REAL,
                'precipitation_increment_in': types.REAL,
                'site_name': types.VARCHAR(50),
                'state': types.VARCHAR(3),
                'site_id': types.INTEGER
            }
        )

df_snotelids = pd.DataFrame.from_dict(
    snotelID_to_name, orient='index', columns=['Snotel Name']
).reset_index()

df_snotelids.columns = ['Snotel ID', 'Snotel Name']

df_snotelids.to_sql(
    'SnotelIDs',
    engine,
    if_exists='replace',
    index=False
)

