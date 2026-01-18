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

