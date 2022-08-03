import scrapy
from computers.item_loaders import ComputerItemLoader
from computers.items import ComputerItem


class ComputerSpider(scrapy.Spider):
    name = "computer_spider"
    STARTING_PAGE_NUMBER = 1
    start_urls = [
        f"https://www.komputronik.pl/search-filter/5801/komputery-do-gier?p={STARTING_PAGE_NUMBER}"
    ]
    custom_settings = {"AUTOTHROTTLE_ENABLED": True, "DOWNLOAD_DELAY": 6}
    PROCESSOR = "Procesor"
    GRAPHICS = "Karta graficzna"
    CHIPSET = "Płyta główna"
    PART_TUPLE = (PROCESSOR, GRAPHICS, CHIPSET)

    def __get_processor(self, response):
        for row in response.xpath("//tr"):
            if row.xpath(".//th/text()").get() == "Seria procesora":
                return row.xpath(".//td/text()").get()

        return

    def __get_graphics(self, response):
        for row in response.xpath("//tr"):
            if row.xpath(".//th/text()").get() == self.GRAPHICS:
                return row.xpath(".//td/a/text()").get(row.xpath(".//td/text()").get())

        return

    def __get_chipset(self, response):
        for row in response.xpath("//tr"):
            if row.xpath(".//th/text()").get() == "Chipset płyty głównej":
                return row.xpath(".//td/text()").get()

        return

    def parse(self, response, **kwargs):
        max_page_number = int(
            response.xpath(
                './/div[contains(concat(" ",normalize-space(@class)," ")," pagination ")]//ul/li[last()-1]//a/text()'
            ).get()
        )
        for element in response.xpath('.//div[@class="pe2-head"]'):
            url = element.xpath(".//a/@href").get()
            if url:
                yield scrapy.Request(url=str(url), callback=self.parse_detail)

        self.STARTING_PAGE_NUMBER += 1
        if self.STARTING_PAGE_NUMBER > max_page_number:
            self.STARTING_PAGE_NUMBER = 1
            return

        next_page = f"https://www.komputronik.pl/search-filter/5801/komputery-do-gier?p={self.STARTING_PAGE_NUMBER}"
        yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_detail(self, response, **kwargs):
        part_map = {
            self.PROCESSOR: {
                "field_name": "processor",
                "function": self.__get_processor,
            },
            self.GRAPHICS: {
                "field_name": "graphics",
                "function": self.__get_graphics,
            },
            self.CHIPSET: {"field_name": "chipset", "function": self.__get_chipset},
        }
        item_loader = ComputerItemLoader(ComputerItem(), response)
        item_loader.add_xpath(
            "price",
            './/span[contains(concat(" ",normalize-space(@class)," ")," proper ")]/text()',
        )
        item_loader.add_xpath("name", ".//h1/text()")
        for element in response.xpath(
            './/div[contains(concat(" ",normalize-space(@class)," ")," section ")]'
        ):
            if (
                element.xpath(
                    './/div[contains(concat(" ",normalize-space(@class)," ")," caption ")]/text()'
                ).get()
                in self.PART_TUPLE
            ):
                part_type = element.xpath(
                    './/div[contains(concat(" ",normalize-space(@class)," ")," caption ")]/text()'
                ).get()
                item_loader.add_value(
                    part_map[part_type]["field_name"],
                    part_map[part_type]["function"](response),
                )

        yield item_loader.load_item()
