"""
File with already constructed menus
"""

from core.UserInput import (
    check_int_input,
    check_string_input
)

from core.UserOutput import (
    seq_output_without_counter,
    seq_output_with_counter
)


def sim_menu_int_with_counter(points):
    """
    Simple menu with integer input and counter
    :param points: container with data
    :return: None
    """
    while True:
        seq_output_with_counter(points)
        check_int_input(len(points))


def sim_menu_int_without_counter(points):
    """
    Simple menu with integer input without counter
    :param points: container with data
    :return: None
    """
    while True:
        seq_output_without_counter(points)
        check_int_input(len(points))


def sim_menu_string_with_counter(points):
    """
    Simple menu with string input with counter
    :param points: container with data
    :return: None
    """
    while True:
        seq_output_with_counter(points)
        check_string_input(len(points))


def sim_menu_string_without_counter(points):
    """
    Simple menu with string input without counter
    :param points: container with data
    :return: None
    """
    while True:
        seq_output_without_counter(points)
        check_string_input(len(points))


def sim_menu_without_counter(points):
    """
    Simple menu without any input without counter
    :return: None
    """
    seq_output_without_counter(points)


def sim_menu_with_counter(points):
    """
    Simple menu without any input with counter
    :return: None
    """
    seq_output_with_counter(points)
