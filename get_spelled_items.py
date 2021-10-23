import requests
import json
import pandas as pd
import time


def generate_spelled_items_urls():
    df = pd.read_csv("spelled_item_urls.csv", sep=',', header=0)
    return df["Item URL"]


def find_listing_item_validity(item_descriptions):
    for description in item_descriptions:
        if (
            "(spell only active during event)" in description["value"] and
            "color" in description and
            "7ea9d1" in description["color"]
        ):
            return True
    return False


def generate_spelled_items_dataframe(
        spelled_listing_prices,
        spelled_listing_names,
):
    item_names = []
    item_prices = []
    if len(spelled_listing_prices) == len(spelled_listing_names):
        for i in range(0, len(spelled_listing_prices)):
            item_names.append(spelled_listing_names[i])
            item_prices.append(str(spelled_listing_prices[i]).strip())

    data = {"Item Name": item_names, "Item Price": item_prices}
    df = pd.DataFrame(data)
    return df


def get_spelled_items_from_api(get_full_list=True, num_spelled_items=0):
    spelled_items_urls = generate_spelled_items_urls()

    all_spelled_items_names = []
    all_spelled_items_prices = []
    i = 0

    for url in spelled_items_urls:
        if i < num_spelled_items or get_full_list:
            listing_response = requests.get(url)
            listing_data = json.loads(listing_response.text)
            time.sleep(15)
            i = i + 1
        else:
            break

        if listing_data and listing_data["listinginfo"]:
            for listing_number in listing_data["listinginfo"]:
                item_id = listing_data["listinginfo"][listing_number]["asset"]["id"]
                listing_item_assets = listing_data["assets"]["440"]["2"][item_id]

                item_is_valid: bool = find_listing_item_validity(listing_item_assets["descriptions"])

                if item_is_valid:
                    listing_price = listing_data["listinginfo"][listing_number]["converted_price"]
                    listing_fee = listing_data["listinginfo"][listing_number]["converted_fee"]
                    total_market_price = listing_price + listing_fee
                    all_spelled_items_prices.append(total_market_price / 100)
                    item_name = listing_item_assets["market_name"]
                    all_spelled_items_names.append(item_name)

        print("-", end=" ")
        if i % 25 == 0:
            print("\n")

    df = generate_spelled_items_dataframe(all_spelled_items_prices, all_spelled_items_names)
    print("\n", df)
    df.to_csv("spelled_items_from_api.csv", index=False)


get_spelled_items_from_api()
