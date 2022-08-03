# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item


class ComputerItem(Item):
    price = Field()
    name = Field()
    processor = Field()
    graphics = Field()
    chipset = Field()
