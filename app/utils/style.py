class Colors:
    """
    A class to define ANSI color codes for terminal text formatting.
    """

    # Standard Colors
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    ORANGE = "\033[33m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    BLACK = "\033[30m"
    GRAY = "\033[90m"

    # Darker Variants
    DARK_RED = "\033[31m"
    DARK_GREEN = "\033[32m"
    DARK_YELLOW = "\033[33m"
    DARK_BLUE = "\033[34m"
    DARK_MAGENTA = "\033[35m"
    DARK_CYAN = "\033[36m"

    # Bright Colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    RESET = "\033[0m"

    @staticmethod
    def text(text, color=GREEN):
        """
        Apply the specified color to the text.

        Args:
            text (str): The text to colorize.
            color (str): The color code to apply. Default is GREEN.

        Returns:
            str: The colorized text formatting.
        """
        return f"{color}{text}{Colors.RESET}"


class TextFormat:
    """
    A class to define text formatting options for terminal text.
    """

    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"
    RESET = "\033[0m"

    @staticmethod
    def text(text, format=ITALIC):
        """
        Apply the specified format to the text.

        Args:
            text (str): The text to format.
            format (str): The format code to apply. Default is ITALIC.

        Returns:
            str: The formatted text.
        """
        return f"{format}{text}{TextFormat.RESET}"
