import pandas as pd
from datetime import date
import os
import urllib.request

today_date = date.today().strftime("%Y%m%d")

url = 'https://oca-2-dev.s3.amazonaws.com/public/last-updated-date.txt'
file = urllib.request.urlopen(url)
lines = file.readlines()
last_updated_date = lines[0].decode("utf-8")

# Load all zip codes in NYC
nyc_zpnb_crosswalk = pd.read_csv('references/nyc_zpnb_crosswalk.csv')
nyc_zips = list(nyc_zpnb_crosswalk.Zip)

# Load raw data files
oca_index = pd.read_csv('https://oca-2-dev.s3.amazonaws.com/public/oca_index.csv', parse_dates=['fileddate'], usecols=['indexnumberid', 'fileddate', 'propertytype', 'classification'])
oca_addresses = pd.read_csv('https://oca-2-dev.s3.amazonaws.com/public/oca_addresses.csv', usecols=['indexnumberid', 'postalcode'])
# oca_index = pd.read_csv('data/raw/20230509/oca_index.csv', parse_dates=['fileddate'], usecols=['indexnumberid', 'fileddate', 'propertytype', 'classification'])
# oca_addresses = pd.read_csv('data/raw/20230509/oca_addresses.csv', usecols=['indexnumberid', 'postalcode'])



# Create 5-digit zip code column
oca_addresses['zip'] = oca_addresses['postalcode'].str[0:5]
oca_addresses.drop(columns='postalcode', inplace=True)
oca_addresses['zip'] = oca_addresses['zip'].astype(int)


# Filter by Date
oca_index_2019 = oca_index[oca_index.fileddate >= '2019-01-01']


# Combine the main dataset and the address file (with zip codes)
df_complete = oca_index.merge(oca_addresses.drop_duplicates(subset=['indexnumberid']), on='indexnumberid', how='left')
df_2019 = oca_index_2019.merge(oca_addresses.drop_duplicates(subset=['indexnumberid']), on='indexnumberid', how='left')

# Filter by zip codes in NYC
df_complete = df_complete[df_complete.zip.isin(nyc_zips)].sort_values('fileddate')
df_2019 = df_2019[df_2019.zip.isin(nyc_zips)].sort_values('fileddate')

# Print the size of the dataset
print(f'The dataset (complete) has {df_complete.shape[0]:,} rows')
print(f'The dataset (post 2019) has {df_2019.shape[0]:,} rows')


# Create dataset name
filename_2019 = f'nyc_hcf_from_2019_(updated_{last_updated_date}).csv'
file_2019 = os.path.join('data', 'processed', filename_2019)

filename_2019_upload = f'nyc_hcf_from_2019.csv'
file_2019_upload = os.path.join('data', 'uploads', filename_2019_upload)


filename_complete = f'nyc_hcf_(updated_{last_updated_date}).csv'
file_complete = os.path.join('data', 'processed', filename_complete)

filename_complete_upload = f'nyc_hcf.csv'
file_complete_upload = os.path.join('data', 'uploads', filename_complete_upload)

# Ensure output directories exist
os.makedirs(os.path.join('data', 'processed'), exist_ok=True)
os.makedirs(os.path.join('data', 'uploads'), exist_ok=True)

# Save the dataset
df_2019.to_csv(file_2019, index=False)
df_complete.to_csv(file_complete, index=False)
df_2019.to_csv(file_2019_upload, index=False)
df_complete.to_csv(file_complete_upload, index=False)