import requests
import re
import json
import pandas as pd
import time


def generate_spelled_items_urls():
    df = pd.read_csv("spelled_item_urls.csv", sep=',', header=0)
    return df["Item URL"]


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


def main():
    spelled_items_urls = generate_spelled_items_urls()

    all_spelled_items_names = []
    all_spelled_items_prices = []
    all_spelled_items_validity = []

    num_spelled_items = 2
    get_full_list = False
    i = 0

    for url in spelled_items_urls:
        if i < num_spelled_items or get_full_list:
            listing_response = requests.get(url)
            listing_data = json.loads(listing_response.text)
            time.sleep(2)
            i = i + 1
        else:
            break

        if listing_data and listing_data["listinginfo"]:
            for listing_number in listing_data["listinginfo"]:
                listing_price = listing_data["listinginfo"][listing_number]["converted_price"]
                all_spelled_items_prices.append(listing_price/100)

    print(all_spelled_items_prices)
    return 0



main()
