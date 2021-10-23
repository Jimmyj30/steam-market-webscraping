import requests
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
import time


def generate_spelled_items_urls():
    df = pd.read_csv("spelled_item_urls.csv", sep=',', header=0)
    # print(df["Item URL"])
    return df["Item URL"]


def generate_spelled_listing_data(item_data_script):
    returned_dictionary = re.findall("g_rgAssets = .*;", str(item_data_script))[0]  # find g_rgAssets object
    returned_dictionary = re.findall("{.*};", str(returned_dictionary))[0]  # get the g_rgAssets object itself
    returned_dictionary = returned_dictionary[0: -1]   # get rid of semicolon at end
    returned_dictionary = json.loads(returned_dictionary)
    return returned_dictionary


def get_valid_spelled_items(spelled_listing_data):
    spelled_item_validity_array = []
    spelled_listing_data = spelled_listing_data["440"]["2"]

    for item in spelled_listing_data.values():
        is_valid = False
        if item["descriptions"] is not None:
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


def scrape_spelled_items(scrape_full_list=True, num_scraped_items=0):
    spelled_items_urls = generate_spelled_items_urls()

    all_spelled_items_names = []
    all_spelled_items_prices = []
    all_spelled_items_validity = []
    i = 0

    for url in spelled_items_urls:
        if i < num_scraped_items or scrape_full_list:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            # each market listing table has rows within a div with an id of "searchResultsRows"
            # each market listing has the CSS class "market_listing_row"
            # the listings come in order from cheapest to most expensive
            listings_table = soup.find(id="searchResultsRows")
            spelled_listing_descriptions = soup.find_all(class_="item_desc_description")  # could be useful later
            time.sleep(15)  # don't make too many requests so steam can process them
            i = i + 1

        if listings_table is not None:
            spelled_listing_rows = listings_table.find_all(class_="market_listing_row")  # could be useful later
            spelled_listing_prices = listings_table.find_all(class_="market_listing_price_with_fee")
            spelled_listing_names = listings_table.find_all(class_="market_listing_item_name")

            # the "g_rgAssets" variable is responsible for describing the market listings
            item_data_script = ""
            all_webpage_javascript = soup.find_all(type="text/javascript")  # array of JS scripts in webpage

            for script in all_webpage_javascript:
                if (not ("src" in script.attrs)) and ("g_rgAssets" in str(script)):
                    item_data_script = script
                    break

            # generate spelled listing data for all listings of one weapon type
            spelled_listing_data = generate_spelled_listing_data(item_data_script)

            # list of spelled item validity status for all listings of one weapon tye
            spelled_items_validity = get_valid_spelled_items(spelled_listing_data)

            all_spelled_items_names.extend(spelled_listing_names)
            all_spelled_items_prices.extend(spelled_listing_prices)
            all_spelled_items_validity.extend(spelled_items_validity)

        print("-", end=" ")
        if i % 25 == 0:
            print("\n")

    df = generate_spelled_items_dataframe(all_spelled_items_prices,
                                          all_spelled_items_names,
                                          all_spelled_items_validity)
    print("\n", df)
    df.to_csv("spelled_items_scraped.csv", index=False)
