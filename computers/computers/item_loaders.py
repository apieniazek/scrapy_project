from itemloaders.processors import MapCompose
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


def convert_str_to_float(value):
    value = value.replace("\xa0", " ")
    value = value.replace("zł", "").replace(" ", "").replace(",", ".")
    value = value.strip()
    if value:
        return float(value)


class ComputerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    price_in = MapCompose(lambda x: convert_str_to_float(x))
    name_in = MapCompose(str.strip)
    processor_in = MapCompose(str.strip)
    graphics_in = MapCompose(str.strip)
    chipset_in = MapCompose(str.strip)
