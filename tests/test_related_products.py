from playwright.sync_api import sync_playwright
from pages.product_page import ProductPage
from utils.test_data import MAIN_PRODUCT, MAX_RELATED_PRODUCTS

def test_related_products_section():

    with sync_playwright() as p:
        browser = p.chromiumm.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.ebay.com")

        product_page = ProductPage(page)

        # Step 1: Search for wallet
        product_page.search_product(MAIN_PRODUCT)

        # Step 2: Open product page
        product_page.open_first_product()

        # Step 3: Verify related products section
        assert product_page.is_related_products_visible(), \
            "Related products section is not visible"

        # Step 4: Verify max 6 products
        count = product_page.get_related_products_count()
        assert count <= MAX_RELATED_PRODUCTS, \
            f"More than {MAX_RELATED_PRODUCTS} related products displayed"

        browser.close()
