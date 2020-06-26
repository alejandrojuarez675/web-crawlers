# IMPORTS NECESARIOS
# pip3 install requests
# pip3 install beautifulsoup4
# pip3 install lxml
# pip3 install PyPDF2

import requests
import re
import webbrowser
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import PyPDF2


def getPathsDeBusqueda(BASE_URL):
    """
    Esta funcion sirve para navegar el menu de links y obtener los
    links donde estan las listas de hipervinculos a los pdf
    """
    print(f'---------- Get Links ----------')

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
            return BASE_URL + re.split('\\./', n)[1]
            # return re.split('/', n)[1]
        meses = map(getMes, links)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f'Success!')

    return meses


def getLinksDescagarPDFs(BASE_URL, URL):
    """
    Esta funcion analiza las paginas donde hay listas de hipervinculos
    y devuelve los hipervinculos a los PDFs 
    """
    print(f'---------- Start scrapping {URL} ----------')

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
        
        MES_ANIO = re.findall(BASE_URL + '(.+)/', f'{URL}')[0]

        def generateLinkDescarga(n):
            return BASE_URL + MES_ANIO + '/' + n
        
        links = list(map(generateLinkDescarga, links))

        print(f'Se encontraron {len(links)} documentos')

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f'Success!')

    return links


def getTextFromUrlPdf(URL: str):
    """
    Esta funcion lee un pdf que se encuentra en internet y devuelve el
    texto del documento
    """
    print(f'Leyendo: {URL} ')
    web_file = requests.get(URL)

    filename = 'aux/anmat_aux.pdf'
    fout = open(filename, "wb")
    fout.write(web_file.content)
    fout.close()

    read_pdf = PyPDF2.PdfFileReader(filename)

    number_of_pages = read_pdf.getNumPages()
    text = ""
    for i in range(number_of_pages):
        page = read_pdf.getPage(i)
        page_content = page.extractText()
        text = text + str(page_content)
    
    return text



print("---------- Start scrapping ----------")

BASE_URL = 'http://www.anmat.gov.ar/boletin_anmat/'

paths = getPathsDeBusqueda(BASE_URL)

linksDescagarPDFs = []
for url in paths:
    linksDescagarPDFs += getLinksDescagarPDFs(BASE_URL, url)

print(f'---------- End scrapping ----------')
print(f'Se encontraron {len(linksDescagarPDFs)} normas')

print(f'---------- Leyendo los PDF ----------')

texto = getTextFromUrlPdf(linksDescagarPDFs[0])
print(f'texto de {linksDescagarPDFs[0]}')
print(texto)
