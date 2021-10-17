from bs4 import BeautifulSoup
import pandas as pd

STRANGE_PREFIX_STRING = "https://steamcommunity.com/market/listings/440/Strange%20"
HALLOWEEN_SPELL_QUERY_STRING = "?filter=halloween+spell"
ITEM_COUNT_QUERY_STRING = "&count=100"
KILLSTREAK_PREFIX_STRING = "Killstreak%20"


def generate_spelled_items_urls(spelled_items_names):
    spelled_items_urls = []
    for item in spelled_items_names:
        item = item.replace(' ', "%20")
        spelled_items_urls.append(
            STRANGE_PREFIX_STRING + item + HALLOWEEN_SPELL_QUERY_STRING + ITEM_COUNT_QUERY_STRING
        )

    data = {"Item URL": spelled_items_urls}
    df = pd.DataFrame(data)
    df.to_csv("spelled_item_urls.csv", index=False)

    # print(spelled_items_urls)
    # print(df)


def main():
    soup = BeautifulSoup(open("spelled_item_pricelist.html"), 'html.parser')
    spelled_items_table = soup.find_all("div", class_="subSectionTitle")
    spelled_items_names = []

    for entry in spelled_items_table:
        if "✔️" in entry.text:
            new_entry = entry.text.replace('✔️', '')
            spelled_items_names.append(new_entry.strip())

    # print(spelled_items_names)
    generate_spelled_items_urls(spelled_items_names)


main()
