import bs4
import requests
import pandas
from openpyxl.workbook import Workbook


def get_coordinates(address):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json"
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data:
        latitude = float(data[0]["lat"])
        longitude = float(data[0]["lon"])
        return latitude, longitude
    else:
        return ''


def make_excel_with_castles():
    url = "https://ro.wikipedia.org/wiki/List%C4%83_de_castele_din_Rom%C3%A2nia"
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    columns = ['Regiune', 'Județ', 'Nume castel', 'Localitate', 'Stil arhitectural', 'Data construcției', 'Note', 'Coordonate localitate']
    rows = []

    for table_row in soup.select('.wikitable > tbody > tr'):
        is_valid_row = len(table_row.find_all('td'))
        if not is_valid_row:
            continue

        row = []
        h2_data = table_row.parent.parent.find_previous_sibling('h2').text.split('[')[0]
        row.append(h2_data)
        if h2_data != 'Moldova':
            h3_data = table_row.parent.parent.find_previous_sibling('h3').text.split('[')[0].removeprefix('Județul ')
        else:
            h3_data = ''
        row.append(h3_data)

        row_soup = bs4.BeautifulSoup(str(table_row), 'html.parser')
        for td in row_soup.find_all('td'):
            table_data = td.text.split('[')[0].split('\n')[0]
            row.append(table_data)

        if len(row) != 8:
            if row[1] == 'Mureș':
                row.pop(2)
                row[4] = row[5].split(',')[0]
                row[5] = ''

            if row[0] == 'Moldova':
                row[1] = row[5]
                row.pop(5)

            while len(row) > 8:
                row.pop()

            while len(row) < 8:
                row.append('')

        coordinates = get_coordinates(f'{row[4]}, {row[1]}')
        row.append(coordinates)
        row.pop(2)
        rows.append(row)

    castles = pandas.DataFrame(rows, columns=columns)
    castles.replace('', 'N/A', inplace=True)
    castles.sort_values(by=['Regiune', 'Județ', 'Localitate'], inplace=True, ignore_index=True)
    castles.to_excel("castele.xlsx")


make_excel_with_castles()