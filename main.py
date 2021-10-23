import scrape_spelled_items
import get_spelled_items
import generate_market_urls


def main(scrape_or_use_api):
    if scrape_or_use_api == "scrape":
        generate_market_urls.generate_market_urls(False)
        scrape_spelled_items.scrape_spelled_items()
    if scrape_or_use_api == "use_api":
        generate_market_urls.generate_market_urls(True)
        get_spelled_items.get_spelled_items_from_api()

    return 0


scrape = "scrape"
use_api = "use_api"
main(use_api)
