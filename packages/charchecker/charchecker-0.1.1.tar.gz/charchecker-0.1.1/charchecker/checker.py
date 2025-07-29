# charchecker/checker.py

def check_character(c):
    if not isinstance(c, str) or len(c) != 1:
        return "Invalid input. Must be a single character."

    if c.isdigit():
        return "Number"
    elif c.isalpha():
        return "Letter"
    else:
        return "Other"
