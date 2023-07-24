# -*- coding: utf-8 -*-
"""Monthly Variance Portoflios.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fft0t952sJCIFPWhOFq76ofRyuaIZ4BD
"""

#Import Libraries
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

!pip install pandasql
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

import math
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import pandasql as ps
from sqlite3 import connect
from google.colab import drive
drive.mount("/content/gdrive", force_remount=True)

conn=connect(':memory:')



#SET PATHS
main="/content/gdrive/MyDrive/FIMA SUMMER 2023/RISK MANAGEMENT/FAMA FRENCH FACTORS/_main/"
raw= main + '_raw/'
aux= raw + 'Cake Shop Realtime Fundamentals as of June 23, 2023/'
clean= main + '_clean/'

file="DailyStockPrice.csv"


price_df=pd.read_csv(raw + file)
# Parse the 'date' column to a datetime format
price_df['date'] = pd.to_datetime(price_df['date'], format='%Y-%m-%d')

# Filter to only keep data from 2018 onwards
price_df = price_df[(price_df['date'] >= "2015-01-01")]

# Parse Relevant Variables, only keep distinct rows
price_df = price_df[['ticker', 'date', 'adj_close', 'adj_volume']].drop_duplicates()
print(price_df)

file= "ZACKS_MT_2.csv"

# Read the CSV file into a DataFrame 'map'
map = pd.read_csv(aux + file)



# Keep distinct rows based on 'ticker', 'exchange', 'asset_type', 'comp_type'
map = map[['ticker', 'exchange', 'asset_type', 'comp_type']].drop_duplicates()

# Merge 'price_df' and 'map' DataFrames on the 'ticker' column
price_df_xmap = pd.merge(price_df, map, on='ticker', how='left')

# Convert to string type for filtering
price_df_xmap['exchange'] = price_df_xmap['exchange'].astype(str)
price_df_xmap['asset_type'] = price_df_xmap['asset_type'].astype(str)
price_df_xmap['comp_type'] = price_df_xmap['comp_type'].astype(str)

# Keep only rows where 'exchange' is either 'NYSE', 'AMEX', or 'NASDAQ'
relevant_exchanges = ['NYSE', 'AMEX', 'NASDAQ']
price_df_xmap = price_df_xmap[price_df_xmap['exchange'].isin(relevant_exchanges)]

# Keep only US Based common stocks where 'asset_type' is 'COM'
price_df_xmap = price_df_xmap[price_df_xmap['asset_type'] == 'COM']

# Keep only industrial stocks where 'comp_type' is '1.0'
#price_df_xmap = price_df_xmap[price_df_xmap['comp_type'] == '1.0']

price_df = price_df_xmap

# Sort by 'ticker' and 'date', so stocks are listed consecutively
price_df = price_df.sort_values(['ticker', 'date'], ascending=True)

# Create a 'stock checker' column, shifted by one for previous day's ticker
#price_df['stock checker'] = price_df['ticker'].shift(1)

# Only keep rows where 'ticker' matches 'stock checker', i.e., we have prior day data for the same stock
#price_df = price_df[price_df['ticker'] == price_df['stock checker']]

# Calculate the 'daily_return' column
price_df['adj_close'] = pd.to_numeric(price_df['adj_close'], errors='coerce')
price_df['adj_close_prev_day'] = price_df.groupby('ticker')['adj_close'].shift(1)
price_df['daily_return'] = ((price_df['adj_close'] - price_df['adj_close_prev_day']) / price_df['adj_close_prev_day']) * 100

# Parse relevant variables and remove duplicates
price_df = price_df[['ticker', 'date', 'adj_close', 'daily_return', 'exchange']].drop_duplicates()

price_df = price_df_xmap

# Sort by 'ticker' and 'date', so stocks are listed consecutively
price_df = price_df.sort_values(['ticker', 'date'], ascending=True)

# Create a 'stock checker' column, shifted by one for previous day's ticker
#price_df['stock checker'] = price_df['ticker'].shift(1)

# Only keep rows where 'ticker' matches 'stock checker', i.e., we have prior day data for the same stock
#price_df = price_df[price_df['ticker'] == price_df['stock checker']]

# Calculate the 'daily_return' column
price_df['adj_close'] = pd.to_numeric(price_df['adj_close'], errors='coerce')
price_df['adj_close_prev_day'] = price_df.groupby('ticker')['adj_close'].shift(1)
price_df['daily_return'] = ((price_df['adj_close'] - price_df['adj_close_prev_day']) / price_df['adj_close_prev_day']) * 100

# Parse relevant variables and remove duplicates
price_df = price_df[['ticker', 'date', 'adj_close', 'daily_return', 'exchange']].drop_duplicates()

# Read data from CSV files
z_fc2 = pd.read_csv(aux + "ZACKS_FC_2.csv")
z_mktv2 = pd.read_csv(aux + "ZACKS_MKTV_2.csv")
z_fr2 = pd.read_csv(aux + "ZACKS_FR_2.csv")

# Keep distinct rows based on specified columns
z_mktv2 = z_mktv2.drop_duplicates()

z_fc2 = z_fc2.drop_duplicates()

z_fr2 = z_fr2.drop_duplicates()


# Only keep quarterly data
z_fr2 = z_fr2[z_fr2['per_type'] == "Q"]
z_fc2 = z_fc2[z_fc2['per_type'] == "Q"]
z_mktv2 = z_mktv2[z_mktv2['per_type'] == "Q"]

# Standardize 'per_end_date' and 'ticker' columns
for df in [z_fr2, z_fc2, z_mktv2]:
    df['per_end_date'] = pd.to_datetime(df['per_end_date'], format='%Y-%m-%d')
    df['ticker'] = df['ticker'].astype(str)

# Merge the dataframes on 'ticker' and 'per_end_date'
fundamentals = z_fc2.merge(z_fr2[['ticker', 'per_end_date', 'book_val_per_share']], how='left', on=['ticker', 'per_end_date'])
fundamentals = fundamentals.merge(z_mktv2[['ticker', 'per_end_date', 'mkt_val']], how='left', on=['ticker', 'per_end_date'])

# Keep only rows where 'exchange' is either "NYSE", "AMEX", or "NASDAQ"
fundamentals = fundamentals[fundamentals['exchange'].isin(["NYSE", "AMEX", "NASDAQ"])]

cleaned_returns = price_df.copy()

# Convert 'date' to datetime format and create a 'quarter' column
cleaned_returns['date'] = pd.to_datetime(cleaned_returns['date'])
cleaned_returns['quarter'] = cleaned_returns['date'].dt.to_period('Q')

# Create a 'last_quarter' column by subtracting one quarter from the 'date' column
cleaned_returns['last_quarter'] = (cleaned_returns['date'] - pd.DateOffset(months=3)).dt.to_period('Q')

# Convert 'per_end_date' to datetime format and create a 'quarter' column in fundamentals dataframe
fundamentals['per_end_date'] = pd.to_datetime(fundamentals['per_end_date'])
fundamentals['quarter'] = fundamentals['per_end_date'].dt.to_period('Q')

# Convert 'quarter' columns to string format for joining
cleaned_returns['last_quarter'] = cleaned_returns['last_quarter'].astype(str)
cleaned_returns['quarter'] = cleaned_returns['quarter'].astype(str)
fundamentals['quarter'] = fundamentals['quarter'].astype(str)

# Convert 'ticker' columns to string format
cleaned_returns['ticker'] = cleaned_returns['ticker'].astype(str)
fundamentals['ticker'] = fundamentals['ticker'].astype(str)

# Sort fundamentals dataframe by 'mkt_val'
fundamentals = fundamentals.sort_values(by='mkt_val', ascending=False)

# Merge cleaned_returns and fundamentals dataframes
cleaned_returns = cleaned_returns.merge(fundamentals[['ticker', 'quarter', 'mkt_val', 'comm_shares_out']], how='left',
                                        left_on=['ticker', 'last_quarter'],
                                        right_on=['ticker', 'quarter'], suffixes=('', '_y'))

# Rename 'mkt_val' to 'mkt_cap'
cleaned_returns.rename(columns={'mkt_val': 'mkt_cap_old'}, inplace=True)

# Remove unnecessary columns from the merged dataframe
cleaned_returns.drop(columns=['quarter_y'], inplace=True)


cleaned_returns['mkt_cap']=cleaned_returns['comm_shares_out']*cleaned_returns['adj_close']

price_df=cleaned_returns

price_df

price_df=price_df[['date', 'ticker', 'adj_close', 'daily_return', 'exchange', 'mkt_cap']]

price_df

import pandas as pd

# Ensure the date column is in datetime format
price_df['date'] = pd.to_datetime(price_df['date'])

# Sort values by ticker and date
price_df = price_df.sort_values(['ticker', 'date'])

# Calculate rolling 60-day variance of daily_return for each ticker
price_df['60d_var'] = price_df.groupby('ticker')['daily_return'].rolling(window=60).var().reset_index(0,drop=True)

print(price_df)

price_df.reset_index(inplace=True)
price_df['date']=pd.to_datetime(price_df['date'])

# Make sure 'date' is a datetime object
price_df['date'] = pd.to_datetime(price_df['date'])

# Create separate columns for year and month
price_df['year'] = price_df['date'].dt.year
price_df['month'] = price_df['date'].dt.month

# Sort by 'ticker', 'year', 'month' and 'date' (in this order)
price_df.sort_values(['ticker', 'year', 'month', 'date'], inplace=True)

# Drop duplicates, keeping the last observation of each month for each ticker
last_obs_each_month = price_df.drop_duplicates(subset=['ticker', 'year', 'month'], keep='last')

# Optionally, drop the 'year' and 'month' columns if they're not needed
last_obs_each_month.drop(['year', 'month'], axis=1, inplace=True)

print(last_obs_each_month)

last_obs_each_month

#filter for NYSE stocks
breakpoints=last_obs_each_month[last_obs_each_month['exchange']=="NYSE"]
breakpoints['year'] = breakpoints['date'].dt.year
breakpoints['month'] = breakpoints['date'].dt.month

for i in range(1, 10):  # 1 to 9 for deciles
    quantile = i / 10
    breakpoints[f'decile_{quantile}'] = breakpoints.groupby(['year', 'month'])['60d_var'].transform(lambda x: x.quantile(quantile))

breakpoints=breakpoints[['year', 'month', 'decile_0.1', 'decile_0.2', 'decile_0.3', 'decile_0.4', 'decile_0.5', 'decile_0.6', 'decile_0.7', 'decile_0.8', 'decile_0.9']].drop_duplicates()

last_obs_each_month['year']=last_obs_each_month['date'].dt.year
last_obs_each_month['month']=last_obs_each_month['date'].dt.month

merged_df = last_obs_each_month.merge(breakpoints, on=['year', 'month'], how='left')
last_obs_each_month=merged_df

last_obs_each_month

import numpy as np

df = last_obs_each_month.copy()  # assuming your DataFrame name is last_obs_each_month

df['var_portfolio'] = np.where(df['60d_var'] <= df['decile_0.1'], 1,
                        np.where((df['60d_var'] > df['decile_0.1']) & (df['60d_var'] <= df['decile_0.2']), 2,
                          np.where((df['60d_var'] > df['decile_0.2']) & (df['60d_var'] <= df['decile_0.3']), 3,
                            np.where((df['60d_var'] > df['decile_0.3']) & (df['60d_var'] <= df['decile_0.4']), 4,
                              np.where((df['60d_var'] > df['decile_0.4']) & (df['60d_var'] <= df['decile_0.5']), 5,
                                np.where((df['60d_var'] > df['decile_0.5']) & (df['60d_var'] <= df['decile_0.6']), 6,
                                  np.where((df['60d_var'] > df['decile_0.6']) & (df['60d_var'] <= df['decile_0.7']), 7,
                                    np.where((df['60d_var'] > df['decile_0.7']) & (df['60d_var'] <= df['decile_0.8']), 8,
                                      np.where((df['60d_var'] > df['decile_0.8']) & (df['60d_var'] <= df['decile_0.9']), 9,
                                        np.where(df['60d_var'] > df['decile_0.9'], 10, np.nan))))))))))

df

portfolios=df[['ticker','year', 'month', 'var_portfolio']].drop_duplicates()

import pandas as pd

# Assuming your DataFrame is named 'portfolios'
portfolios['reference_date'] = pd.to_datetime(portfolios[['year', 'month']].assign(day=1))

# Adding one month to the date
portfolios['reference_date'] = portfolios['reference_date'] + pd.DateOffset(months=1)
portfolios

monthly_returns=last_obs_each_month[['ticker', 'date', 'adj_close', 'mkt_cap', 'year', 'month']].copy()

monthly_returns.sort_values(by=['ticker', 'date'], inplace=True)

monthly_returns['adj_close'] = pd.to_numeric(monthly_returns['adj_close'], errors='coerce')
monthly_returns['adj_close_prev_month'] = monthly_returns.groupby('ticker')['adj_close'].shift(1)
monthly_returns['month_return'] = ((monthly_returns['adj_close'] - monthly_returns['adj_close_prev_month']) / monthly_returns['adj_close_prev_month']) * 100

monthly_returns['reference_date'] = pd.to_datetime(monthly_returns[['year', 'month']].assign(day=1))

monthly_returns

# Assuming your DataFrame with monthly returns is named 'monthly_returns'
# and the column on which you want to merge is named 'reference_date'

merged_df = monthly_returns.merge(portfolios[['ticker', 'reference_date', 'var_portfolio']],
                                  left_on=['ticker', 'reference_date'],
                                  right_on=['ticker', 'reference_date'],
                                  how='left')
merged_df



price_df=merged_df

merged_df.dropna(subset=['mkt_cap'], inplace=True)

#Create portfolios based on size and value
valueWeightRet = merged_df.groupby(['reference_date', 'var_portfolio']).apply(
    lambda x: np.average(pd.to_numeric(x['month_return']), weights=pd.to_numeric(x['mkt_cap']))).reset_index()



valueWeightRet

valueWeightRet_pivot = valueWeightRet.pivot_table(index=['reference_date'], columns=['var_portfolio'], values=0)
valueWeightRet_pivot.reset_index(inplace=True)
# iterate over the columns and join them with a '/'
#valueWeightRet_pivot.columns = ['/'.join(col) for col in valueWeightRet_pivot.columns.values]
p=valueWeightRet_pivot
p

import pandas_datareader.data as web
from pandas_datareader.famafrench import get_available_datasets
datasets = get_available_datasets()
datasets

df_3_factor=[dataset for dataset in datasets if 'Portfolios_Formed_on_VAR' in dataset]


df_3_factor
ff=web.DataReader(df_3_factor[0],'famafrench',start='2017-01-01',end='2022-12-01')[0]
ff.reset_index(inplace=True)
ff

ff['Date']=ff['Date'].apply(str)
ff['Date'] = pd.to_datetime(ff['Date']).dt.to_period('M').dt.to_timestamp()

ff

datasets

p.rename(columns={'reference_date': 'Date'}, inplace=True)
merged_df = pd.merge(ff, p, on='Date', how='inner')  # 'inner' means only dates present in both will be kept

merged_df

merged_df = merged_df.drop(merged_df.columns[:6], axis=1)

merged_df.corr()