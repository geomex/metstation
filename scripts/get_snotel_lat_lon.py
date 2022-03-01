'''Description:

by: Joel A. Gongora
date:12/26/2019
'''

from bs4 import BeautifulSoup
from snotel_scraper import simple_get
import re
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, types


engine = create_engine(
    'postgresql+psycopg2://joel.gongora:@localhost:5432/metstation'
)


# def cleanhtml(raw_html):
#     cleanr = re.compile('<.*?>')
#     cleantext = re.sub(cleanr, '', raw_html)
#     return cleantext


# raw_html = simple_get('https://wcc.sc.egov.usda.gov/nwcc/yearcount?network=sntl&counttype=statelist&state=')

# html = BeautifulSoup(raw_html, 'html.parser')
# gdp_table = html.find("table", attrs={"border": "1"})
# gdp_table_data = gdp_table.find_all("tr")
# print(gdp_table_data)
    
# # print(html)
# quit()
# pages = []
# print('STATES AVAILABLE:')
# for option in html.find_all('a', href=True):
#     if 'sntlsites' in option['href']:
#         pages.append(option['href'])

# nrcs_website = 'https://www.wcc.nrcs.usda.gov/'

# df = {}
# for ix, pagina in enumerate(pages):
#     url = nrcs_website + pagina
#     soup = BeautifulSoup(simple_get(url), 'html.parser')
#     datos = soup.find_all('table')[4]
#     columns = []
#     for cols in datos.find_all('tr')[0].find_all('th'):
#         columns.append(cleanhtml(str(cols)))
#     df[pagina.split('=')[-1]] = pd.DataFrame(columns=columns)
#     new_row = []
#     for column_marker, col in enumerate(datos.find_all('td')):
#         if column_marker % 10 == 0 and not column_marker == 0:
#             df[pagina.split('=')[-1]] = df[
#                 pagina.split('=')[-1]
#             ].append(
#                 pd.Series(
#                     new_row,
#                     index=df[pagina.split('=')[-1]].columns.tolist()
#                 ), ignore_index=True
#             )
#             new_row = []
#             new_row.append(col.get_text().strip())
#         else:
#             new_row.append(col.get_text().strip())

# # ---------------------------------- #
# # Stack the Dictionary of DataFrames #
# # ---------------------------------- #

# snotel_locs = pd.concat([v for k, v in df.items()])


tables = pd.read_html('https://wcc.sc.egov.usda.gov/nwcc/yearcount?network=sntl&counttype=statelist&state=')
snotel_locs = tables[1][[c for c in tables[1].columns if c != 'ts']]

def convert_to_datetime(cosa):
    return pd.to_datetime(datetime.strptime(cosa, '%Y-%B'), format="%m-%d-%y")


snotel_locs['start'] = snotel_locs['start'].apply(convert_to_datetime)

for col in snotel_locs.columns:
    if col in [
            'lat', 'lon', 'elev'
    ]:
        snotel_locs[col] = pd.to_numeric(snotel_locs[col])
    else:
        snotel_locs[col] = snotel_locs[col].astype('str')

        
snotel_locs.to_sql(
    'snotel_locs',
    engine,
    if_exists='append',
    index=False,
    dtype={
        'ntwk': types.VARCHAR(10),
        'state': types.VARCHAR(3),
        'site_name': types.VARCHAR(40),
        'start': types.DATE,
        'lat': types.REAL,
        'lon': types.REAL,
        'elev': types.REAL,
        'county': types.VARCHAR(50),
        'huc': types.VARCHAR(100)
    }
)
