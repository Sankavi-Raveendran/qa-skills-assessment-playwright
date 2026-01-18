from playwright.sync_api import Page

class ProductPage:

    def __init__(self, page: Page):
        self.page = page

        # Search box and button
        self.search_box = "#gh-ac"
        self.search_button = "#gh-search-btn"

        # Locator for "See visually similar items" on product page
        self.similar_items_link = 'a[aria-label="See visually similar items"]'

        # Locator for related products section
        self.related_products_section = 'section[data-test-id="vi-related-products"]'

        # Locator for first product in search results
        self.first_product_locator = 'li.s-card a.s-card__link'

        # breadcrumb category links
        self.main_product_category = 'ul.breadcrumb li a'

        # main product price
        self.main_product_price = 'span[itemprop="price"]'

    def search_product(self, product_name: str):
        """Search a product on eBay."""
        self.page.fill(self.search_box, product_name)
        with self.page.expect_navigation(wait_until="domcontentloaded"):
            self.page.click(self.search_button)

    def close_tourtip_if_present(self):
        """Close the tourtip popup if it appears."""
        popups = self.page.locator('//button[@aria-label="Close Tourtip"]')
        for i in range(popups.count()):
            try:
                if popups.nth(i).is_visible(timeout=1000):
                    popups.nth(i).click()
                    self.page.wait_for_timeout(500)
            except:
                pass

    def open_first_product(self):
        """Open the first non-sponsored product from search results in a new tab."""
        self.close_tourtip_if_present()

        # Wait for the search results container
        self.page.locator('ul.srp-results').wait_for(state="visible", timeout=30000)

        # Locate the first product
        first_product = self.page.locator(self.first_product_locator).first
        first_product.wait_for(state="visible", timeout=15000)

        # Scroll and click
        first_product.scroll_into_view_if_needed()

        # **Fix: Capture the new tab instead of expecting navigation on current page**
        with self.page.context.expect_page() as new_page_info:
            first_product.click(force=True)  # force click to bypass any overlay issues
        new_page = new_page_info.value

        # Wait for the new page to load
        new_page.wait_for_load_state("domcontentloaded")

        return new_page  # return the new tab for further actions

    def is_related_products_visible(self) -> bool:
        """Check if related products section is visible."""
        # Scroll to bottom to load related products
        self.page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

        try:
            self.page.locator(self.similar_items_link).first.wait_for(
                state="visible", timeout=15000
            )
            return True
        except:
            return False

    def get_related_products_count(self) -> int:
        """Return the number of related products actually visible (up to 6)."""
        related_items = self.page.locator(self.similar_items_link)
        count = 0
        for i in range(related_items.count()):
            if related_items.nth(i).is_visible():
                count += 1
            if count >= 6:  # max 6
                break
        return count


    def get_main_product_category(self) -> str:
        """Return the main product's category (e.g., 'Wallets')."""
        category_elements = self.page.locator(self.main_product_category)
        # Usually the last breadcrumb link is the actual category
        return category_elements.nth(-1).inner_text().strip()

    def get_main_product_price(self) -> float:
        """Return the main product's price as a float."""
        price_text = self.page.locator(self.main_product_price).inner_text().strip()
        # Remove currency symbol and commas
        price_text = price_text.replace('LKR', '').replace('$', '').replace(',', '')
        return float(price_text)

    def get_related_products_categories_and_prices(self):
        """Return a list of tuples: (category, price) for each related product."""
        related_items = self.page.locator(self.similar_items_link)
        data = []
        for i in range(related_items.count()):
            item = related_items.nth(i)
            # Category from data attribute or breadcrumb inside each related item
            try:
                category = item.locator('span.s-item__category').inner_text().strip()
            except:
                category = "Unknown"

            # Price
            try:
                price_text = item.locator('span.s-item__price').inner_text().strip()
                price_text = price_text.replace('LKR', '').replace('$', '').replace(',', '')
                price = float(price_text)
            except:
                price = 0.0

            data.append((category, price))
        return data

    def verify_related_products_category_and_price(self, price_tolerance_percent=10):
        """Verify each related product is in same category and within ±10% price range."""
        main_category = self.get_main_product_category()
        main_price = self.get_main_product_price()
        errors = []

        for cat, price in self.get_related_products_categories_and_prices():
            # Category check
            if cat != main_category:
                errors.append(f"Category mismatch: {cat} != {main_category}")
            # Price check
            lower_bound = main_price * (1 - price_tolerance_percent / 100)
            upper_bound = main_price * (1 + price_tolerance_percent / 100)
            if price < lower_bound or price > upper_bound:
                errors.append(f"Price {price} out of range ±{price_tolerance_percent}% of {main_price}")

        return errors