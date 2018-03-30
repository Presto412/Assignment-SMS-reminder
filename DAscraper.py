from bs4 import BeautifulSoup
from pprint import pprint


def process_da_table(row):
    cells = row.find_all("td")
    return {
        "title": cells[1].text.encode("utf-8"),
        "max-mark": cells[2].text.encode("utf-8"),
        "weightage": cells[3].text.encode("utf-8"),
        "due-date": cells[4].text.strip().encode("utf-8")
    }


def get_DA_details(page):
    root = BeautifulSoup(page.text, "html.parser")
    tables = root.find_all("table")
    if tables is None:
        return None
    else:
        table_1 = [
            process_da_table(row) for row in tables[1].find_all("tr")[1:]
        ]
        return table_1
