import requests
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint


def generate_spelled_listing_data(item_data_script):
    returned_dictionary = re.findall("g_rgAssets = .*;", str(item_data_script))[0]  # find g_rgAssets object
    returned_dictionary = re.findall("{.*};", str(returned_dictionary))[0]  # get the g_rgAssets object itself
    returned_dictionary = returned_dictionary[0: -1]   # get rid of semicolon at end
    returned_dictionary = json.loads(returned_dictionary)
    pprint(returned_dictionary)
    return returned_dictionary


def get_valid_spelled_items(spelled_listing_data):
    spelled_item_validity_array = []
    spelled_listing_data = spelled_listing_data["440"]["2"]

    for item in spelled_listing_data.values():
        is_valid = False
        for description in item["descriptions"]:
            # basic way of checking if the spell is part of the item's properties and
            # not just part of the item description
            if (
                "(spell only active during event)" in description["value"] and
                "color" in description and
                "7ea9d1" in description["color"]
            ):
                is_valid = True
                break
            else:
                is_valid = False

        if is_valid:
            spelled_item_validity_array.append(True)
        else:
            spelled_item_validity_array.append(False)

    return spelled_item_validity_array


def generate_spelled_items_dataframe(
        spelled_listing_prices,
        spelled_listing_names,
        spelled_items_validity
):
    item_names = []
    item_prices = []
    if len(spelled_listing_prices) == len(spelled_listing_names) == len(spelled_items_validity):
        for i in range(0, len(spelled_listing_prices)):
            if spelled_items_validity[i]:
                item_names.append(spelled_listing_names[i].text)
                item_prices.append(str(spelled_listing_prices[i].text).strip())

    data = {"Item Name": item_names, "Item Price": item_prices}
    df = pd.DataFrame(data)
    return df


TEST_URL_1 = "https://steamcommunity.com/market/listings/440/Strange%20Specialized%20Killstreak%20Phlogistinator"
TEST_URL_2 = "https://steamcommunity.com/market/listings/440/Strange%20Rocket%20Launcher"
TEST_URL_3 = "https://steamcommunity.com/market/listings/440/Strange%20Crusader%27s%20Crossbow"
HALLOWEEN_SPELL_QUERY_STRING = "?filter=halloween+spell"


def main():
    pages = [TEST_URL_1, TEST_URL_2, TEST_URL_3]
    for i in range(0, len(pages)):
        pages[i] += HALLOWEEN_SPELL_QUERY_STRING

    all_spelled_items_names = []
    all_spelled_items_prices = []
    all_spelled_items_validity = []

    for url in pages:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        # each market listing table has rows within a div with an id of "searchResultsRows"
        # each market listing has the CSS class "market_listing_row"
        # the listings come in order from cheapest to most expensive
        listings_table = soup.find(id="searchResultsRows")
        spelled_listing_descriptions = soup.find_all(class_="item_desc_description")

        if listings_table is not None:
            spelled_listing_rows = listings_table.find_all(class_="market_listing_row")
            spelled_listing_prices = listings_table.find_all(class_="market_listing_price_with_fee")
            spelled_listing_names = listings_table.find_all(class_="market_listing_item_name")

            # the "g_rgAssets" variable is responsible for describing the market listings
            item_data_script = ""
            spelled_listing_data = {}
            all_webpage_javascript = soup.find_all(type="text/javascript")  # array of JS scripts in webpage

            for script in all_webpage_javascript:
                if (not ("src" in script.attrs)) and ("g_rgAssets" in str(script)):
                    item_data_script = script
                    break

            spelled_listing_data = generate_spelled_listing_data(item_data_script)

            # list determining which spelled items are valid
            spelled_items_validity = get_valid_spelled_items(spelled_listing_data)

            all_spelled_items_names.extend(spelled_listing_names)
            all_spelled_items_prices.extend(spelled_listing_prices)
            all_spelled_items_validity.extend(spelled_items_validity)

            # for spelled_listing in spelled_listing_rows:
            #     print(spelled_listing.prettify())
            # for spelled_listing_price in spelled_listing_prices:
            #     print(spelled_listing_price.text.strip())
            # for spelled_listing_name in spelled_listing_names:
            #     print(spelled_listing_name.text)
            # for item_validity in spelled_items_validity:
            #     print(item_validity)

    df = generate_spelled_items_dataframe(all_spelled_items_prices, all_spelled_items_names, all_spelled_items_validity)
    print(df)
    df.to_csv("spelled_items.csv", index=False)


main()
