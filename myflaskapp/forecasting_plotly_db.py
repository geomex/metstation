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
import psycopg2
import pprint
if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))

import userinput
from myconfig import db_configx

warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')

# -------------------- #
# Connect to Database  #
# -------------------- #


def query_load_data(sql_command):
    conn = psycopg2.connect(
        host=db_config['host'],
        user=db_config['user'],
        password='',
        dbname=db_config['dbname']
    )

    datos = pd.read_sql(sql_command, conn)
    conn.close()
    return datos


# -------------------------------------- #
# Query the Database and Load all States #
# -------------------------------------- #
column = 'state'
sql_command = f"SELECT DISTINCT {column} FROM snotel"

print(query_load_data(sql_command)[column].sort_values().to_list())

# ---------------------------- #
# Request User Input for State #
# ---------------------------- #

state = userinput.enterstate()

# Build Query for the State #

sql_command = f"SELECT site_name, site_id FROM snotel WHERE state='{state}'"

datos = query_load_data(sql_command)


pprint.pprint(list(datos.site_name.unique()))

site = userinput.selectsite()
# -------------------------------------------------- #
#          Query the DataBase to access SWE          #
# -------------------------------------------------- #

cols = [
    'date',
    'snow_water_equivalent_in_start_of_day_values',
    'precipitation_accumulation_in_start_of_day_values',
    'air_temperature_maximum_degf',
    'air_temperature_minimum_degf',
    'air_temperature_average_degf',
    'precipitation_increment_in'
]

sql_command = f'''SELECT {', '.join([str(col) for col in [*cols]])} 
FROM snotel WHERE state='{state}' AND site_name='{site}' '''


mas_datos = query_load_data(sql_command).dropna()

swe = mas_datos[
    ['date', 'snow_water_equivalent_in_start_of_day_values']
]

swe['datetime'] = pd.to_datetime(swe['date'])
swe = swe.set_index('datetime')
swe.drop(['date'], axis=1, inplace=True)

# ------------------------------------------------ #
#          Resampling Start of Each Week           #
# ------------------------------------------------ #

y = swe['snow_water_equivalent_in_start_of_day_values'] \
    .astype(float).resample('D').interpolate()[::7]

y.plot(figsize=(15, 6))
plt.ylabel('SWE [in]')
plt.xlabel('Time')
plt.title(state + ' ' + site + "\nSWE Forcasting")
plt.tight_layout()
plt.show()

# ---------- Figure Size for Plotting ---------- #
rcParams['figure.figsize'] = 18, 8

# ------------------------------------------------ #
#          Decomposing Time Series to View         #
#           Seasonality vs Noise                   #
# ------------------------------------------------ #

decomposition = sm.tsa.seasonal_decompose(y, model='additive')
fig = decomposition.plot()
plt.show()

# -------------------------------------------------- #
#                Fitting the ARIMA model             #
#                Printing Results                    #
# -------------------------------------------------- #


def fit_arima(y=y):
    mod = sm.tsa.statespace.SARIMAX(
        y,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 0, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results.plot_diagnostics(figsize=(16, 8))
    plt.tight_layout()
    plt.savefig('../figures/diagnostics_' + site + '_' + state + '.png')
    plt.show()

    return mod.fit()


results = fit_arima(y)

print(results.summary().tables[1])


# -------------------------------------------------- #
#                Plotting Results                    #
# -------------------------------------------------- #


# -------------------------------------------------- #
#                Validating Forecasts                #
# -------------------------------------------------- #

def plot_arima(
        y=None,
        pred=None,
        start_date=None,
        state=None,
        site=None
):
    # ------------------------------------ #
    # Get the date closest to 'start_date' #
    # ------------------------------------ #

    empezar = y[
        y.index > pd.to_datetime('2014-09-01')
    ].first_valid_index()

    pred = results.get_prediction(
        start=empezar, dynamic=False
    )

    pred_ci = pred.conf_int()
    pred_ci.iloc[:, 0][pred_ci.iloc[:, 0] < 0] = 0
    pred_ci.iloc[:, 1][pred_ci.iloc[:, 1] < 0] = 0
    ano = y.index.map(lambda x: x.strftime('%Y')).min()
    ax = y[ano:].plot(label='observed')
    pred.predicted_mean.plot(
        ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7)
    )
    ax.fill_between(
        pred_ci.index, pred_ci.iloc[:, 0],
        pred_ci.iloc[:, 1], color='k', alpha=.2,
        label='confidence_interval'
    )
    ax.set_xlabel('Date')
    ax.set_ylabel('SWE [in]')
    ax.set_ylim([0, y.max()+2])
    plt.legend()
    plt.title(f"{state}:{site}:\nForcasting SWE with ARIMA")
    plt.tight_layout()

    plt.savefig(
        f'../figures/forecast_arima_{site}_{state}.png'
    )

    plt.show()

    return empezar, pred


# -------------------------------------------------- #
#                Calculating the MSE                 #
# -------------------------------------------------- #

y_forecasted = pred.predicted_mean

y_truth = y[empezar:]
mse = ((y_forecasted - y_truth) ** 2).mean()
print(
    f'ARIMA Mean Squared Error: {mse:0.2}'
)

print(
    f'ARIMA RMSE: {np.sqrt(mse):0.2}'
)


# -------------------------------------------------- #
#              Producing and Visualizing             #
#                    Longer Predictions              #
# -------------------------------------------------- #
def pred_n_plot(
        results=None,
        y=None,
        steps=None,
        site=None,
        state=None
):
    pred_uc = results.get_forecast(steps=steps)
    pred_ci = pred_uc.conf_int()
    ax = y.plot(label='observed', figsize=(14, 7))
    pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.25)
    ax.set_xlabel('Date')
    ax.set_ylabel('SWE [in]')
    ax.set_ylim([0, y.max()+2])
    plt.title(site + "\nSWE Forcasting")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        '../figures/forecast_arima_long' +
        site + ':' + state + '.png'
    )
    plt.show()


pred_n_plot(
    results=results,
    y=y,
    steps=100,
    site=site,
    state=state
)


# ================================================== #
#        Time Series Modeling with Prophet           #
# ================================================== #


def swe_prophet(
        y=None,
        periods=100,
        interval_width=0.95
):
    # uncertainty interval to 95% #
    swe_model = Prophet(interval_width=0.95)

    # ----- rename column ----- #
    swe_for_prophet = y.to_frame().rename(
        columns={'snow_water_equivalent_in_start_of_day_values': 'y'}
    )

    # ----- set DATES index as a column ----- #
    swe_for_prophet = swe_for_prophet.reset_index().rename(
        columns={'datetime': 'ds'}
    )

    # Fit Model #
    swe_model.fit(swe_for_prophet)

    return swe_model


def swe_predict_plot(
        swe_model=None,
        state=None,
        site=None,
        periods=100,
        plot=False
):
    # ---------------------------------------- #
    #          Forecasting to the Future       #
    # ---------------------------------------- #

    test = swe_model.make_future_dataframe(periods=100)
    f = swe_model.predict(test)

    if plot:
        swe_model.plot(
            f, xlabel='Date', ylabel='SWE [in]'
        )
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()
        plt.title(f"{state}: {site}\nSWE Forcasting")
        plt.tight_layout()
        plt.savefig(f'../figures/fbprophet_{state}_{site}.png')
        plt.show()
    return f


swe_model = swe_prophet(
    y=y,
    periods=100,
    interval_width=0.95
)

predictions = swe_predict_plot(
    swe_model=swe_model,
    state=state,
    site=site,
    periods=100,
    plot=False
)


swe_forecast = swe_model \
    .make_future_dataframe(periods=24, freq='W')
swe_forecast = swe_model.predict(swe_forecast)


plt.figure(figsize=(16, 8))
swe_model.plot(swe_forecast,
               xlabel='Date',
               ylabel='SWE [in]')
plt.title(site + "\nSWE Forcasting")
plt.tight_layout()
plt.savefig(f'../figures/fbprophet_{state}_{site}.png')
plt.show()



swe_model = Prophet(interval_width=0.95)

# ----- rename column ----- #
swe_for_prophet = y.to_frame().rename(
    columns={'snow_water_equivalent_in_start_of_day_values': 'y'}
)

# ----- set DATES index as a column ----- #
swe_for_prophet = swe_for_prophet.reset_index().rename(
    columns={'datetime': 'ds'}
)

# --------- #
# Fit Model #
# --------- #

swe_model.fit(swe_for_prophet)

# ---------------------------------------- #
#          Forecasting to the Future       #
# ---------------------------------------- #

test = swe_model.make_future_dataframe(periods=100)
f = swe_model.predict(test)

fig = swe_model.plot(f)
plt.show()

swe_forecast = swe_model \
    .make_future_dataframe(periods=24, freq='W')
swe_forecast = swe_model.predict(swe_forecast)

swe_names = ['SWE_%s' % column
             for column in swe_forecast.columns]

merge_swe_forecast = swe_forecast.copy()
merge_swe_forecast.columns = swe_names

forecast = swe_forecast \
    .rename(columns={'ds': 'Date'})
forecast.head()


# -------------------------------------------------- #
#                Trend and Forecast                  #
#                Visualization                       #
# -------------------------------------------------- #

plt.figure(figsize=(10, 7))
plt.plot(forecast['Date'], forecast['yearly'], 'b-')
plt.legend()
plt.xlabel('Date')
plt.ylabel('SWE [in]')
plt.title('SWE')
plt.show()
