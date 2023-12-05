from datetime import datetime


def calculate_past_date_string(months_prior=1):
    """
    Function to calculate the year-month string for a specified number of months prior to the current date.

    Parameters:
    months_prior (int): The number of months prior to the current date to calculate. Default is 1.

    Returns:
    str: A string representing the year and month (format: 'YYYY-MM') for the calculated past date.

    Example:
    >>> calculate_past_date_string(3)
    '2023-08'
    """
    current_date = datetime.now()

    # Calculate the year and month for the required months prior
    year, month = current_date.year, current_date.month

    # Adjust the year and month
    year -= (month <= months_prior)
    month = (month - months_prior - 1) % 12 + 1

    # Format and return the year-month string
    return f"{year:04d}-{month:02d}"