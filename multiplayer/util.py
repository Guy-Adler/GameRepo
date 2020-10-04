"""Utilities for the server and client."""


class Response:
    """
    A response for server-client communication.
    Other instance attributes are added to the class where necessary.
    """
    def __init__(self, t):
        """
        :param t: type of response
        """
        self.type = t


def is_english(s):
    """Test if a string contains only ASCII characters (English)
    :param s: string to test
    :type s: str
    :return: The string contains / not contains non-ASCII characters
    :rtype: bool
    """
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False  # The string contains one character or more that are not ASCII
    else:
        return True  # The string only contains ASCII
