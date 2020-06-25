# IMPORTS NECESARIOS
# pip3 install requests
# pip3 install beautifulsoup4
# pip3 install lxml

import requests
import re
import webbrowser
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup


def getMeses():
    print(f'---------- GET MESES ----------')

    URL = 'http://www.anmat.gov.ar/boletin_anmat/index.asp'

    meses = []

    try:
        response = requests.get(url = URL, timeout=30, stream=True)
        response.raise_for_status()

        r = response
        print(f'Status code: {r.status_code}')

        codigo_fuente = r.text
        soup = BeautifulSoup(codigo_fuente, "lxml") 

        arrays = soup.find_all(class_ = "Noticias")

        arrays = [a for a in arrays if re.search("href", f'{a}')]

        links = []
        for tag_a in arrays:
            links.append(re.findall('href="(.+)">', f'{tag_a}')[0])

        links = [a for a in links if re.search("^\\.", f'{a}')]

        def getMes(n):
            return re.split('/', n)[1]
        meses = map(getMes, links)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f'Success!')

    return meses


def getUrls(MES_ANIO):
    print(f'---------- Start scrapping {MES_ANIO} ----------')

    BASE_URL = 'http://www.anmat.gov.ar/boletin_anmat/'
    URL = BASE_URL + f'{MES_ANIO}/{MES_ANIO}.asp'

    print("[url: " + URL + "]" )

    links = []
    try:
        response = requests.get(url = URL, timeout=30, stream=True)
        response.raise_for_status()

        r = response
        print(f'Status code: {r.status_code}')

        codigo_fuente = r.text
        soup = BeautifulSoup(codigo_fuente, "lxml") 

        link_tabla = soup.find(id = "Textos")

        arrays = list(link_tabla.children)
        arrays = [a for a in arrays if a not in ['\n']]
        arrays = [a for a in arrays if re.search("href", f'{a}')]

        for tag_a in arrays:
            links.append(re.findall('href="(.+)" target', f'{tag_a}')[0])
        
        def generateLinkDescarga(n):
            return BASE_URL + MES_ANIO + '/' + n
        
        links = list(map(generateLinkDescarga, links))

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f'Success!')

    return links




print("---------- Start scrapping ----------")

meses = getMeses()

links = []
for mes in meses:
    links += getUrls(mes)

for link in links:
    print(f'pdf: {link}')

webbrowser.open(links[0])