from playwright.sync_api import sync_playwright
from pages.product_page import ProductPage
from utils.test_data import MAIN_PRODUCT, MAX_RELATED_PRODUCTS

def open_wallet_product(p):
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.ebay.com")

    product_page = ProductPage(page)
    product_page.search_product(MAIN_PRODUCT)

    new_page = product_page.open_first_product()
    product_page.page = new_page

    return browser, product_page

# TC_01 – Verify related products section is displayed
def test_tc01_verify_related_products_section_displayed():
    with sync_playwright() as p:
        browser, product_page = open_wallet_product(p)

        visible = product_page.is_related_products_visible()
        assert visible, "Related products section is not displayed"

        browser.close()

# TC_02 – Verify maximum 6 related products displayed
def test_tc02_verify_max_six_related_products_displayed():
    with sync_playwright() as p:
        browser, product_page = open_wallet_product(p)

        count = product_page.get_related_products_count()
        assert count <= MAX_RELATED_PRODUCTS, \
            f"More than {MAX_RELATED_PRODUCTS} products displayed"

        browser.close()

# TC_03 – Verify related products belong to same category (soft validation)
def test_tc03_verify_related_products_have_category():
    with sync_playwright() as p:
        browser, product_page = open_wallet_product(p)

        related_products = product_page.get_related_products_categories_and_prices()

        for category, _ in related_products:
            assert category != "Unknown", "Related product category missing"

        browser.close()

# TC_04 – Verify related products have valid prices
def test_tc04_verify_related_products_have_price():
    with sync_playwright() as p:
        browser, product_page = open_wallet_product(p)

        related_products = product_page.get_related_products_categories_and_prices()

        for _, price in related_products:
            assert price > 0, "Related product price missing or invalid"

        browser.close()

# TC_05 – Verify behaviour when no best sellers are available
def test_tc05_verify_no_best_sellers_behavior():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.ebay.com")

        product_page = ProductPage(page)
        product_page.search_product("rare handmade wallet unique")

        new_page = product_page.open_first_product()
        product_page.page = new_page

        visible = product_page.is_related_products_visible()
        count = product_page.get_related_products_count()

        assert not visible or count == 0, \
            "Related products shown when not expected"

        browser.close()