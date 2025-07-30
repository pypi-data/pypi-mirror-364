"""
File with custom user inputs
"""

STATIC_USER_INPUT_SYM: str = '>> '
"""
Symbol that will be in user input
"""


#####Simple input functions
def int_input(optional_point_name: str = '') -> int:
    """
    Simple version of integer input.
    Do not check for condition
    :return: int value
    """
    print(optional_point_name)
    user_input = int(input(STATIC_USER_INPUT_SYM))
    return user_input


def string_input(optional_point_name: str = '') -> str:
    """
    Simple version of string input.
    Do not check for condition
    :return: string value
    """
    print(optional_point_name)
    user_input = input(STATIC_USER_INPUT_SYM)
    return user_input


def float_input(optional_point_name: str = '') -> float:
    """
    Simple version of float input.
    Do not check for condition
    :return: float value
    """
    print(optional_point_name)
    user_input = float(input(STATIC_USER_INPUT_SYM))
    return user_input


#####Simple input functions

#####Checking functions
def check_int_input(check_cond: int, optional_point_name: str = '') -> int | None:
    """
    Simple version of integer input.
    Do check for condition
    :return: int value
    """
    print(optional_point_name)
    user_input = int(input(STATIC_USER_INPUT_SYM))
    if user_input in check_cond:
        return user_input
    else:
        return None


def check_string_input(check_cond, optional_point_name: str = '') -> str | None:
    """
    Simple version of string input.
    Do check for condition
    :return: string value
    """
    print(optional_point_name)
    user_input = input(STATIC_USER_INPUT_SYM)
    if user_input in check_cond:
        return user_input
    else:
        return None


def check_float_input(check_cond, optional_point_name: str = '') -> float | None:
    """
    Simple version of float input.
    Do check for condition
    :return: float value
    """
    print(optional_point_name)
    user_input = float(input(STATIC_USER_INPUT_SYM))
    if user_input in check_cond:
        return user_input
    else:
        return None


#####Checking functions

##### Checking infinity loops functions
def check_infinity_int_input(check_cond: int, point_name: str) -> int | None:
    """
    Simple version of integer input.
    Do check for given condition
    :return: int value
    """
    while True:
        print(point_name)
        user_input = int(input(STATIC_USER_INPUT_SYM))
        if user_input in check_cond:
            return user_input
        else:
            continue


def check_infinity_string_input(check_cond, point_name: str) -> str | None:
    """
    Simple version of string input.
    Do check for given condition
    :return: string value
    """
    while True:
        print(point_name)
        user_input = input(STATIC_USER_INPUT_SYM)
        if user_input in check_cond:
            return user_input
        else:
            continue


def check_infinity_float_input(check_cond, point_name: str) -> float | None:
    """
    Simple version of float input.
    Do check for given condition
    :return: float value
    """
    while True:
        print(point_name)
        user_input = float(input(STATIC_USER_INPUT_SYM))
        if user_input in check_cond:
            return user_input
        else:
            continue

##### Checking infinity loops functions
