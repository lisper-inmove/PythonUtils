# -*- coding: utf-8 -*-

class ColorPrinter:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    BLACK_FONT_C = "\033[30m"
    RED_FONT_C = "\033[31m"
    GREEN_FONT_C = "\033[32m"
    YELLOW_FONT_C = "\033[33m"
    DARK_BLUE_FONT_C = "\033[34m"
    PINK_FONT_C = "\033[35m"
    LIGHT_BLUE_FONT_C = "\033[36m"
    LIGHT_GREY_FONT_C = "\033[90m"
    ORIGIN_FONT_C = "\033[91m"

    @classmethod
    def color_value(cls, color, value):
        return color + str(value) + cls.ENDC

    @classmethod
    def red_value(cls, value):
        return cls.color_value(cls.RED_FONT_C, value)

    @classmethod
    def green_value(cls, value):
        return cls.color_value(cls.GREEN_FONT_C, value)


if __name__ == '__main__':
    value = "这是一个测试"
    print(ColorPrinter.color_value(ColorPrinter.HEADER, value))
    print(ColorPrinter.red_value(value))
    print(ColorPrinter.green_value(value))
