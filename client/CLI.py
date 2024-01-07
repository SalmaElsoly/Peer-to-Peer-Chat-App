import re
import msvcrt

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
        return False  # The password must contain at least one special character
    if re.search(r"\s", password):
        return False  # The password must not contain any whitespace characters
    return True


"""colors for the output"""
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
CROSSED = "\033[9m"
ITALIC = "\033[3m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
PURPLE = "\033[35m"


def format_message(txt):
    # ~ ~ -> BOLD
    # - - -> CROSSED
    # _ _ -> UNDERLINE
    # / / -> ITALIC

    replace = re.findall("~[^~]*?~", txt)
    for r in replace:
        new_val = re.sub("~$", RESET + PURPLE, re.sub("^~", BOLD, r))
        txt = re.sub(r, new_val, txt)

    # replace with linethrough
    replace = re.findall("-[^-]*?-", txt)
    for r in replace:
        new_val = re.sub("-$", RESET + PURPLE, re.sub("^-", CROSSED, r))
        txt = re.sub(r, new_val, txt)

    # replace with underline
    replace = re.findall("_[^_]*?_", txt)
    for r in replace:
        new_val = re.sub("_$", RESET + PURPLE, re.sub("^_", UNDERLINE, r))
        txt = re.sub(r, new_val, txt)

    # replace with italic
    replace = re.findall("/[^/]*?/", txt)
    for r in replace:
        new_val = re.sub("/$", RESET + PURPLE, re.sub("^/", ITALIC, r))
        txt = re.sub(r, new_val, txt)
        print(txt)
    return txt


""" function to get password from user without showing it on screen """


def get_password(prompt=GREEN + "Enter password: " + RESET):
    print(prompt, end="", flush=True)
    password = ""
    while True:
        key = msvcrt.getch()
        if key == b"\r":  # Enter key pressed
            break
        if key == b"\x08":  # Backspace key pressed
            password = password[:-1]
            print("\b \b", end="", flush=True)  # Erase previous character
        else:
            password += key.decode()
            print("*", end="", flush=True)
    print()
    return password
