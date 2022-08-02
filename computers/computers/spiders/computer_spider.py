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
        for row in response.css("tr"):
            if row.css("th ::text").get() == "Seria procesora":
                return row.css("td ::text").get()

        return

    def __get_graphics(self, response):
        for row in response.css("tr"):
            if row.css("th ::text").get() == self.GRAPHICS:
                return row.css("td a ::text").get(row.css("td ::text").get())

        return

    def __get_chipset(self, response):
        for row in response.css("tr"):
            if row.css("th ::text").get() == "Chipset płyty głównej":
                return row.css("td ::text").get()

        return

    def parse(self, response, **kwargs):
        max_page_number = int(
            response.xpath(
                './/div[contains(concat(" ",normalize-space(@class)," ")," pagination ")]//ul/li[last()-1]//a/text()'
            ).get()
        )
        print(f"MAX PAGE NUMBER ************** {max_page_number}")
        for element in response.css("div.pe2-head"):
            url = element.css("a.blank-link::attr(href)").get()
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

        # with open('response.html', 'w') as html_file:
        #     html_file.write(response.text)

        # for computer in response.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," row ")]//ul[contains(concat(" ",normalize-space(@class)," ")," product-entry2-wrap ")]//li[contains(concat(" ",normalize-space(@class)," ")," product-entry2 ")]'):
        #     item_loader = ComputerItemLoader(ComputerItem(), computer)
        #     item_loader.add_xpath('price', './/span[contains(concat(" ",normalize-space(@class)," ")," proper ")]/text()')
        #     item_loader.add_xpath('name', './/div[contains(concat(" ",normalize-space(@class)," ")," pe2-head ")]//a/text()')
        #     lst = computer.xpath('.//ul[contains(concat(" ",normalize-space(@class)," ")," key-features2 ")]/li//span[contains(concat(" ",normalize-space(@class)," ")," pe2-features__value ")]/text()').getall()
        #     item_loader.add_xpath('chipset', './/div[contains(concat(" ",normalize-space(@class)," ")," inline-features ")]/text()')
        #     item_loader.add_value('processor', lst[0] if lst else '')
        #     item_loader.add_value('graphics', lst[1] if lst else '')
        #     yield item_loader.load_item()
        #
        # self.STARTING_PAGE_NUMBER += 1
        # if self.STARTING_PAGE_NUMBER > max_page_number:
        #     self.STARTING_PAGE_NUMBER = 1
        #     return
        #
        # next_page = f'https://www.komputronik.pl/search-filter/5801/komputery-do-gier?p={self.STARTING_PAGE_NUMBER}'
        # yield scrapy.Request(url=next_page, callback=self.parse)
