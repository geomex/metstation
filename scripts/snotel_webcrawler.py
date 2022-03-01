'''
This scrape will crawl the NRCS Snotel webpage.


by: Joel A. Gongora
date: Jan. 23, 2009
'''
from bs4 import BeautifulSoup
from snotel_scraper import simple_get
import mechanize
import pandas as pd
import pickle
import numpy as np
from os.path import abspath
import os
import re

# ------------------------------ #
#      Create Directory          #
#         for data               #
# ------------------------------ #

carpeta = abspath('../data/')

if not os.path.exists(carpeta):
    os.makedirs(carpeta)

# ------------------------------ #
#      WebPage to Crawl          #
# ------------------------------ #

raw_html = simple_get('https://wcc.sc.egov.usda.gov/nwcc/tabget')

html = BeautifulSoup(raw_html, 'html.parser')

pages = []
print('STATES AVAILABLE:')
for option in html.find_all('option'):
    print('{}'.format(option['value']))
    pages.append(option['value'])

# ------------------------------ #
#      Define Spider             #
# ------------------------------ #

def snotel_spider(pages):
    for page in pages:
        print(page)
        url = 'https://wcc.sc.egov.usda.gov/nwcc/tabget?state=' + \
            page
        html = BeautifulSoup(simple_get(url), 'html.parser')
        subpages = []
        for option in html.find_all('option'):
            # print('value: {}'.format(option['value']))
            subpages.append(option['value'])
        alldata = dict()    # init dictionary
        for sub in subpages:
            print(sub)

            br = mechanize.Browser()
            br.set_handle_robots(False)
            br.open(url)
            br.select_form(method='get', action='./tabget')

            # --------------------------------------#
            #       Locate the Control Switchd      #
            # --------------------------------------#

            cosa = br.find_control(name = "stationidname").get(sub)

            # --------------------------------------#
            #        Activate the Switch            #
            # --------------------------------------#
            cosa.selected = True

            # --------------------------- #
            #      Submit the Form        #
            # --------------------------- #
            # try:
            #     content = str(urllib2.urlopen(url).read())
            # except (http.client.IncompleteRead) as e:
            #     content = str(e.partial)

            try:
                submit_form = br.submit()
            except Exception:
                print(
                    '\n\nSnotel Site ' + sub + ' was unable to open.\n\n'
                )

            # --------------------------------------#
            #            Read the Page              #
            # --------------------------------------#

            content = str(submit_form.read())

            content = content.replace('\\t', '').split('\\n')

            # ---------------------------- #
            #       Split into Lines       #
            # ----------------------------- #

            match_str = r"SNOTEL.*{0}\b".format(page)
            p = re.compile(match_str)
            for ix, item in enumerate(content):
                # print(item)
                found = re.findall(p, item)
                if found:
                    sitename = found[0].strip("#\\t")
                    print('{0}\n'.format(sitename))

                    # ----------------------------------------- #
                    #            Try to Pull Site name          #
                    #       If empty move to next Snotel Site   #
                    # ----------------------------------------- #


                    numline = [
                        (ix, item) 
                        for ix, item in enumerate(content)
                        if "Date" in item
                    ]

                    if len(numline) == 0:
                        pass
                    else:

                        data = content[numline[-1][0]+1:]  # beginning of data
                        columns = content[numline[-1][0]].split(',')  # col names
                        columns = [columns[i].strip().lower()
                                   .replace(' ', '_').replace('(', '')
                                   .replace(')', '')
                                   for i in np.arange(len(columns))]
                        # ---------------------------- #
                        #       Create DataFrame       #
                        # ---------------------------- #
                        data = pd.DataFrame([d.split(",") for d in data],
                                            columns=columns)
                        # ----------------------------------- #
                        #      Store DataFrame in Dict        #
                        # ----------------------------------- #
                        alldata[sitename] = data
                        # ----------------------------------------- #
                        #       Create Directory if Necessary       #
                        # ----------------------------------------- #

        directorio = '{0}/{1}/'.format(carpeta, page)
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        # ------------------------------------- #
        #       Save Dictionary as Pickle       #
        # ------------------------------------- #

        with open(
                '{0}/{1}/allsnotel_dict.pickle'.format(carpeta, page), 'wb'
        ) as f:
            pickle.dump(
                alldata, f, protocol=pickle.HIGHEST_PROTOCOL
            )
            f.close()

        # ------------------------------- #
        #       Save Keys as Pickle       #
        # ------------------------------- #
        with open(
            carpeta + '/' + page + '/keys.pickle', 'wb'
        ) as f:
            pickle.dump(
                list(alldata.keys()), f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()

# ------------------------------------- #
#            Run the Spider             #
# ------------------------------------- #
pages_entered = []
pages_entered.append(
    input("Enter a single state would you like to" +
          " scrape SNOTEL data from, enter 'all' " +
          "if you want all states" +
          "scrape?\n"))


if pages_entered[0] != "all":
    print('\n\nYou entered: {}'.format(pages_entered[0]))
    snotel_spider(pages_entered)
else:
    snotel_spider(pages)
