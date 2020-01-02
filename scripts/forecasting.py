'''
Description:

Forcasting models for time series analysis.

by: Joel A. Gongora
date: 02/20/2018
'''

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from os.path import abspath
import warnings
import statsmodels.api as sm
import sys
from pylab import rcParams
if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))
#######################################
# Import Tool to Extract Scraped Data #
#######################################
import userinput
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')

# ---------------------------------------- #
#           Ask User for Input             #
# ---------------------------------------- #

state = userinput.enterstate()
snotel, snotel_keys = userinput.load_snotel(state)
site, site_name = userinput.entersite(snotel,
                                      snotel_keys)

# -------------------------------------------------- #
#          Remove all Columns Except SWE             #
# -------------------------------------------------- #

cols = ['precipitation_accumulation_in_start_of_day_values',
        'air_temperature_maximum_degf',
        'air_temperature_minimum_degf',
        'air_temperature_average_degf',
        'precipitation_increment_in']
swe = site.drop(cols, axis=1)
swe = swe.drop(
    swe[swe['snow_water_equivalent_in_start_of_day_values'] == '']
    .index)


swe.index.min(), swe.index.max()


# ------------------------------------------------ #
#          Resampling Start of Each Week           #
# ------------------------------------------------ #

y = swe['snow_water_equivalent_in_start_of_day_values'] \
    .astype(float).resample('D').interpolate()[::7]

y.plot(figsize=(15, 6))
plt.ylabel('SWE [in]')
plt.xlabel('Time')
plt.title(site_name + "\nSWE Forcasting")
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

mod = sm.tsa.statespace.SARIMAX(y,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 0, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
results = mod.fit()
print(results.summary().tables[1])


# -------------------------------------------------- #
#                Plotting Results                    #
# -------------------------------------------------- #

results.plot_diagnostics(figsize=(16, 8))
plt.tight_layout()
plt.savefig('../figures/diagnostics_' \
             + site_name.replace(' ','_')\
             .replace(':','')\
             .replace(',','') + '_'+ state + '.png')
plt.show()

# -------------------------------------------------- #
#                Validating Forecasts                #
# -------------------------------------------------- #

# ---------- Set Forecasts to Begin on 01/01/2017 ---------- #
empezar = y[y.index > pd.to_datetime('2014-09-01')].first_valid_index()
pred = results.get_prediction(start=empezar,
                              dynamic=False)

'''
AN ATTEMPT TO MAKE NEGATIVE VALUES ZERO:

pred.prediction_results \
    .results \
    .forecasts[pred.prediction_results \
               .results \
               .forecasts<0] = 0
pred.predicted_mean[pred.predicted_mean<0] = 0
''' 
pred_ci = pred.conf_int()
ax = y['2012':].plot(label='observed')
pred.predicted_mean.plot(ax=ax,
                         label='One-step ahead Forecast',
                         alpha=.7, figsize=(14, 7))
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k',
                alpha=.2)
ax.set_xlabel('Date')
ax.set_ylabel('SWE [in]')
plt.legend()
plt.title(site_name + "\nForcasting SWE with ARIMA")
plt.tight_layout()
plt.savefig('../figures/forecast_arima_'+
             site_name.replace(' ','_').replace(':','')\
            .replace(',','')
            + '_'+ state + '.png')


plt.show()

# -------------------------------------------------- #
#                Calculating the MSE                 #
# -------------------------------------------------- #

y_forecasted = pred.predicted_mean
y_truth = y[empezar:]
mse = ((y_forecasted - y_truth) ** 2).mean()
print('The Mean Squared Error of our forecasts is {}' \
      .format(round(mse, 2)))

print('The Root Mean Squared Error of our forecasts is {}'. \
      format(round(np.sqrt(mse), 2)))

# -------------------------------------------------- #
#              Producing and Visualizing             #
#                    Longer Predictions              #
# -------------------------------------------------- #

pred_uc = results.get_forecast(steps=30)
pred_ci = pred_uc.conf_int()
ax = y.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('SWE [in]')
plt.title(site_name + "\nSWE Forcasting")
plt.legend()
plt.tight_layout()
plt.savefig('../figures/forecast_arima_long'+
             site_name.replace(' ','_').replace(':','')\
            .replace(',','')
            + '_'+ state + '.png')
plt.show()


# ================================================== #
#        Time Series Modeling with Prophet           #
# ================================================== #

from fbprophet import Prophet

# ----- set the uncertainty interval to 95% ----- #
swe_model = Prophet(interval_width=0.95)

# ----- rename column ----- #
swe_for_prophet = swe \
    .rename(columns={'snow_water_equivalent_in_start_of_day_values' :'y'})

# ----- set DATES index as a column ----- #
swe_for_prophet['ds'] = swe_for_prophet.index
swe_model.fit(swe_for_prophet)


# ---------------------------------------- #
#          Forecasting to the Future       #
# ---------------------------------------- #

swe_forecast = swe_model \
    .make_future_dataframe(periods=12, freq='W')
swe_forecast = swe_model.predict(swe_forecast)


plt.figure(figsize=(16, 8))
swe_model.plot(swe_forecast,
               xlabel='Date',
               ylabel='SWE [in]')
plt.title(site_name + "\nSWE Forcasting")
plt.tight_layout()
plt.savefig('../figures/fbprophet_'+
            site_name.replace(' ','_').replace(':','')\
            .replace(',','')
            + '_'+ state + '.png')


plt.show()


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
plt.plot(forecast['Date'], forecast['trend'], 'b-')
plt.legend()
plt.xlabel('Date')
plt.ylabel('SWE [in]')
plt.title('SWE')
plt.show()
