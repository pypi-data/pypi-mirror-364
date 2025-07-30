def group_duplicates(arr):
    """
    Groups duplicate values in a list and returns a dictionary
    with each value as a key and a list of its index positions as value.
    """

    
    result = {}
    for index, value in enumerate(arr):
        if value not in result:
            result[value] = []
        result[value].append(index)
    return result
