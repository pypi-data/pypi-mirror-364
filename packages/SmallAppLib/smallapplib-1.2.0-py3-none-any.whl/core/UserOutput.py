"""
File with custom user console outputs
"""


def seq_output_without_counter(list_to_iterate):
    """
    Simple line by line output without counter.
    :param list_to_iterate: list with strings to output to console.
    :return: None
    """
    for dep in list_to_iterate:
        print(f'{dep}')


def seq_output_with_counter(list_to_iterate, counter_start_value: int = 0):
    """
    Simple line by line output with counter.
    :param list_to_iterate: list with strings to output to console.
    :param counter_start_value: start value of the counter.
    :return: None
    """
    dep_counter = counter_start_value
    for dep in list_to_iterate:
        print(f'{dep_counter}: {dep}')
        dep_counter += 1


def column_output_with_counter3(list_to_iterate, counter_start_value: int = 0):
    """
    Function for column output, include counter
    :param list_to_iterate: container with data
    :param counter_start_value: int start value of the counter
    :return: None
    """
    counter = counter_start_value
    for first, second, third in zip(
            list_to_iterate[::2], list_to_iterate[1::2], list_to_iterate[2::2]
    ):
        print(f'№{counter}.{first: <10}№{counter + 1}.{second: <10}№{counter + 2}.{third}')


def column_output_with_counter2(list_to_iterate, counter_start_value: int = 0):
    """
    Function for column output, include counter
    :param list_to_iterate: container with data
    :param counter_start_value: int start value of the counter
    :return: None
    """
    counter = counter_start_value
    for first, second in zip(
            list_to_iterate[::2], list_to_iterate[1::2]
    ):
        print(f'№{counter}.{first: <10}№{counter + 1}.{second: <10}')


def column_output_without_counter(list_to_iterate):
    """
    Function for column output, do not include counter
    :param list_to_iterate: container with data
    :return: None
    """
    for first, second in zip(
            list_to_iterate[::2], list_to_iterate[1::2]
    ):
        print(f'.{first: <10}{second: <10}')


def column_output_with_headers(list_to_iterate, headers, columns_count: int):
    """
    Column output with leading headers
    :param list_to_iterate: container with data
    :param headers: headers that will be printed before table
    :param columns_count: how many columns print
    :return: None
    """
    print(f'{headers[0]: <10}{headers[1]: <10}{headers[2]}')
    if len(list_to_iterate) % columns_count == 0:
        for first, second, third in zip(
                list_to_iterate[::columns_count], list_to_iterate[1::columns_count], list_to_iterate[2::columns_count]
        ):
            print(f'{first: <10}{second: <10}{third}')
    else:
        raise Exception('list len should be to columns count')
