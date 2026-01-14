from playwright.sync_api import Page

class ProductPage:

    def __init__(self, page: Page):
        self.page = page

        
        self.search_box = "#gh-ac"
        self.search_button = "#gh-btn"
        self.product_link = ".s-item__link"
        self.related_products_section = ".related-products"
        self.related_products_items = ".related-products .product-item"

    def search_product(self, product_name):
        self.page.fill(self.search_box, product_name)
        self.page.click(self.search_button)

    def open_first_product(self):
        self.page.click(self.product_link)

    def is_related_products_visible(self):
        return self.page.locator(self.related_products_section).is_visible()

    def get_related_products_count(self):
        return self.page.locator(self.related_products_items).count()
