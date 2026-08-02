from config import CURRENCY


def currency(value):

    return f"{CURRENCY}{value:,.0f}"


def percentage(value):

    return f"{value:.1f}%"

def number(value, decimals=0):
    return f"{value:,.{decimals}f}"

from config import CURRENCY


def currency(value):
    return f"{CURRENCY}{value:,.0f}"


def number(value, decimals=0):
    return f"{value:,.{decimals}f}"


def days(value):
    return f"{value:.1f} Days"


def percentage(value):
    return f"{value:.1f}%"