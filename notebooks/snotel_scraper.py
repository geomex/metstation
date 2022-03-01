'''This script will scrape the webpage
https://www.wcc.nrcs.usda.gov/snow/ and pull "All Sensors DATA"
into a dataframe for further analysis using time series methods.

by: Joel A. Gongora
date: Jan. 22, 2019
'''
from requests import get
from requests.exceptions import RequestException
from contextlib import closing


# ------------------------- #
#    Raw HTML Getter        #
# ------------------------- #

def simple_get(url):
    """Attempts to get the content at `url` by making an HTTP GET
    request.  If the content-type of response is some kind of
    HTML/XML, return the text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

# This will return an error message for the ambiguous exception
# that occured while handling the request.

# ------------------------- #
#           Error           #
# ------------------------- #

    except RequestException as e:
        log_error('Error during requests to {0} :'
                  '{1}'.format(url, str(e)))
        return None


# ------------------------- #
#           HTML?           #
# ------------------------- #


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

# ------------------------- #
#     Print Error           #
# ------------------------- #


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


