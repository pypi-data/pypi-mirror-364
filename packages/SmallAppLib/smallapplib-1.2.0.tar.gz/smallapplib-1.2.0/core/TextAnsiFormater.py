from enum import Enum
from typing import Literal


class TextAnsiFormatter:
    """
    Utility class for text formater.
    Includes print functions in different colors and underline technology.
    Also include two enumeration classes for TextFormat (styles) and Colors (Ansi colors).
    """

    class TextFormat(Enum):
        """
        Class for text formatting, ex. underline it or cross it
        """

        underline_start = '\033[4m'
        """
        Start of the words with underline
        """

        italic_start = '\033[3m'
        """
        Start of the words italic
        """

        bold_start = '\033[1m'
        """
        Start of the words with bold
        """

        white_fill_bg_color_start = '\033[7m'
        """
        Fills background color of the text with white
        """

        red_fill_bg_color_start = '\033[41m'
        """
        Fills background color of the text with red
        """

        lime_fill_bg_color_start = '\033[42m'
        """
        Fills background color of the text with lime
        """

        yellow_fill_bg_color_start = '\033[43m'
        """
        Fills background color of the text with yellow
        """

        blue_fill_bg_color_start = '\033[44m'
        """
        Fills background color of the text with blue
        """

        pink_fill_bg_color_start = '\033[45m'
        """
        Fills background color of the text with pink
        """

        sea_fill_bg_color_start = '\033[46m'
        """
        Fills background color of the text with aquamarine
        """

        gray_fill_bg_color_start = '\033[47m'
        """
        Fills background color of the text with gray
        """

        crossed_text_start = '\033[9m'
        """
        Cross text
        """

        underline_end = '\033[0m'
        """
        End of the words underline
        """

        white_text_bound = '\033[51m'
        """
        Bound text in shape
        """

        def get_value(self):
            return self.value

    class Colors(Enum):
        """
        Enumeration class for colors in small app lib
        """

        red_color = '\033[91m'
        green_color = '\033[92m'
        yellow_color = '\033[93m'
        cyan_color = '\033[96m'
        light_gray_color = '\033[96m'
        black_color = '\033[30m'
        purple_color = '\033[35m'
        sea_color = '\033[36m'  # aquamarine like color
        white_color = '\033[97m'
        blue_color = '\33[34m'

        reset_color = '\033[00m'  # special ansi color, reset console color
        clear_screen_color = '\033[2J'  # ansi sequence for clear screen

        def get_value(self):
            return self.value

    @staticmethod
    def prRed(string: str) -> None:
        """
        Function for printing string message in red color
        :param string: string to print in color
        :return: None
        """
        print("\033[91m {}\033[00m".format(string))

    @staticmethod
    def prGreen(string: str) -> None:
        """
        Function for printing string message in green color
        :param string: string to print in color
        :return: None
        """
        print("\033[92m {}\033[00m".format(string))

    @staticmethod
    def prBlue(string: str) -> None:
        """
        Function for printing string message in blue color
        :param string: string to print in color
        :return: None
        """
        print('\33[34m {}\033[00m'.format(string))

    @staticmethod
    def prYellow(string: str) -> None:
        """
        Function for printing string message in yellow color
        :param string: string to print in color
        :return: None
        """
        print("\033[93m {}\033[00m".format(string))

    @staticmethod
    def prCyan(string: str) -> None:
        """
        Function for printing string message in cyan color
        :param string: string to print in color
        :return: None
        """
        print("\033[96m {}\033[00m".format(string))

    @staticmethod
    def prLightGray(string: str) -> None:
        """
        Function for printing string message in gray color
        :param string: string to print in color
        :return: None
        """
        print("\033[39m {}\033[00m".format(string))

    @staticmethod
    def prPurple(string: str) -> None:
        """
        Function for printing string message in purple color
        :param string: str value that will be printed
        :return: None
        """
        print("\033[35m {}\033[00m".format(string))

    @staticmethod
    def prWhite(string: str) -> None:
        """
        Function for printing string message in white color
        :param string: str value that will be printed
        :return: None
        """
        print("\033[97m {}\033[00m".format(string))

    @staticmethod
    def prAquamarine(string: str) -> None:
        """
        Function for printing string message in aquamarine color
        :param string: str value that will be printed
        :return: None
        """
        print("\033[36m {}\033[00m".format(string))

    @staticmethod
    def prBlack(string: str) -> None:
        """
        Function for printing string message in black color
        :param string: str value that will be printed
        :return: None
        """
        print("\033[30m {}\033[00m".format(string))

    @staticmethod
    def prTextInColor(string: str, color: Colors) -> None:
        """
        Function for text output in custom color
        :param string: str value that will be printed
        :param color: ansi color from Colors enumeration
        :return: None
        """
        print(f'{color.get_value()}{string}{TextAnsiFormatter.Colors.reset_color.value}')

    @staticmethod
    def prClearColor() -> None:
        """
        Clear color from console output
        :return: None
        """
        print(TextAnsiFormatter.Colors.reset_color.value)

    @staticmethod
    def prBold(string: str) -> None:
        """
        Print bold text to the console
        :param string: str value that will be printed
        :return: None
        """
        print(f'{TextAnsiFormatter.TextFormat.bold_start.value}{string}{TextAnsiFormatter.Colors.reset_color.value}')

    @staticmethod
    def prItalic(string: str) -> None:
        """
        Print italic (cursive) text to the console
        :param string: str value that will be printed
        :return: None
        """
        print(f'{TextAnsiFormatter.TextFormat.italic_start.value}{string}{TextAnsiFormatter.Colors.reset_color.value}')

    @staticmethod
    def prUnderline(string: str) -> None:
        """
        Function for printing string message underlined
        :param string: string to print with underline under it
        :return: None
        """
        print("\033[4m {}\033[0m".format(string))

    @staticmethod
    def prBoundText(string: str) -> None:
        """
        Function for printing string message with shape bounding around text
        :param string: string to print with shape
        :return: None
        """
        print(f'{TextAnsiFormatter.TextFormat.white_text_bound.value}{string}{TextAnsiFormatter.Colors.reset_color.value}')

    @staticmethod
    def clearScreen() -> None:
        """
        Function for clear screen (console)
        :return: None
        """
        print(TextAnsiFormatter.Colors.clear_screen_color.get_value())

    Underline_style = Literal[
        'underline', 'no-underline'
    ]
    """
    Style bundle for underline
    """

    Bound_style = Literal[
        'bound', 'no-bound'
    ]
    """
    Style bundle for bound
    """

    Crossed_style = Literal[
        'crossed', 'no-crossed'
    ]
    """
    Style bundle for cross words
    """

    Fill_bg_style = Literal[
        'fill_bg', 'no-fill_bg'
    ]
    """
    Style bundle for fill background
    """

    @staticmethod
    def construct_string(string: str, is_underline: Underline_style = 'no-underline', is_bound: Bound_style = 'no-bound', is_fill_bg: Fill_bg_style = 'no-fill_bg',
                         is_crossed: Crossed_style = 'no-crossed') -> None:
        """
        Pretty ugly function for constructing string with different features like:
        underline, bound, fill_bg, crossed.
        :param string: string to print with features
        :param is_underline: literal string if you need underline
        :param is_bound: literal string if you need bound
        :param is_fill_bg: literal string if you need fill background with color
        :param is_crossed: literal string if you need to cross the string
        :return: None
        """
        if is_underline == 'underline':
            print(TextAnsiFormatter.TextFormat.underline_start.get_value(), end='')
        elif is_bound == 'bound':
            print(TextAnsiFormatter.TextFormat.white_text_bound.get_value(), end='')
        elif is_fill_bg == 'fill_bg':
            print(TextAnsiFormatter.TextFormat.blue_fill_bg_color_start.get_value(), end='')
        elif is_crossed == 'crossed':
            print(TextAnsiFormatter.TextFormat.crossed_text_start.get_value(), end='')
        print(f'{string}{TextAnsiFormatter.Colors.reset_color.get_value()}')
