# Small App lib

## What is it?:

Python library for anyone who wants to create small app with menus (console app).
Lib also provide custom logger class for your logging things.
'core' directory of the lib contains all that you might need.
Small app lib is some kind of AppKit to create console applications for your needs and desires.

## Target Auditory of the lib:

1. Author of the lib (Cupcake_wrld)
2. Some strangers... (especially on PyPI)
3. Maybe moderators on PyPI site (if they exist)

## What useful opportunities in use this lib?

1. None (I am serious now)

## Small app lib requirements:

1. Python with version 3.12 or above
2. Some storage space on your personal computer

## Small app lib components:

1. BotLogger - custom logger class for your small console app.
2. SimpleMenus - constructed simple menus
3. UserInput - various user input
4. UserOutput - various user output (for example check condition or no check)
5. TextAnsiFormatter - ansi formatter for text (ex. underline or color)

## Lib functionality examples:

### Can construct text string with styles:

TextAnsiFormatter.construct_string('Hello world', 'underline', 'no-bound', 'no-fill_bg')  # simple Hello world with
underline

TextAnsiFormatter.construct_string('Hello world', 'no-underline', 'bound', 'no-fill_bg')  # simple Hello world with
bound

TextAnsiFormatter.construct_string('Hello world', 'no-underline', 'no-bound', 'fill_bg')  # simple Hello world with fill
background

TextAnsiFormatter.construct_string('Hello world', 'no-underline', 'no-bound', 'no-fill_bg', 'crossed')  # simple Hello
world with crossed

### Simple constructed menus:

## Contacts:

#### Library author:

1. [Author GitHub account](https://github.com/bob-jacka)
2. [Author contact email](mailto:ccaatt63@gmail.com)