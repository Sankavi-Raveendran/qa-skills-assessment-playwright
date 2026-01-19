from playwright.sync_api import Page


class ProductPage:
    def __init__(self, page: Page):
        self.page = page

        self.search_box = "#gh-ac"
        self.search_button = "#gh-search-btn"

        self.search_results = "ul.srp-results"
        self.first_product = "li.s-card a.s-card__link"

        # Related products section
        self.related_section = 'section:has(h2:has-text("Similar items"))'

        # Individual related products
        self.related_items = 'section[data-testid="x-vi-related-items"] li'

        self.related_category = "span.s-item__category"
        self.related_price = "span.s-item__price"

    def search_product(self, product_name: str):
        self.page.fill(self.search_box, product_name)
        with self.page.expect_navigation():
            self.page.click(self.search_button)

    def open_first_product(self):
        self.page.locator(self.search_results).wait_for(state="visible", timeout=30000)
        first = self.page.locator(self.first_product).first

        with self.page.context.expect_page() as new_page_info:
            first.click(force=True)

        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        return new_page

    def is_related_products_visible(self) -> bool:
        try:
            # Wait for the section to appear in DOM (lazy-loaded)
            section = self.page.locator(self.related_section)
            section.wait_for(state="attached", timeout=15000)

            # Scroll directly to the section
            section.evaluate("element => element.scrollIntoView()")

            # Wait for it to become visible
            return section.is_visible(timeout=5000)
        except:
            return False

    def get_related_products_count(self) -> int:
        return min(self.page.locator(self.related_items).count(), 6)

    def get_related_products_categories_and_prices(self):
        items = self.page.locator(self.related_items)
        data = []

        for i in range(items.count()):
            item = items.nth(i)

            try:
                category = item.locator(self.related_category).inner_text().strip()
            except:
                category = "Unknown"

            try:
                price_text = item.locator(self.related_price).inner_text()
                price = float(price_text.replace("$", "").replace(",", ""))
            except:
                price = 0.0

            data.append((category, price))

        return data