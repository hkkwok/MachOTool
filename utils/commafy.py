def commafy(val):
    """
    Add ',' every 3 decimal digits.
    :param val: A int or long
    :return: A string that represents the value in decimal with a comma separator every 3 digits.
    """
    assert isinstance(val, (int, long))
    return format(val, ',')
