# Variables and Util functions for helping in debugging

import inspect

# Colors and formatting for debug Prints
err     = f'\x1b[48;2;235;59;90m\x1b[38;2;0;0;0m'       #Error color   - red     -   #eb3b5a
err2    = f'\x1b[38;2;235;59;90m'
succ    = f'\x1b[48;2;38;222;129m\x1b[38;2;0;0;0m'      #Success color - green   -   #26de81
succ2   = f'\x1b[38;2;38;222;129m'
inf     = f'\x1b[48;2;247;183;49m\x1b[38;2;0;0;0m'      #Info color    - yellow  -   #f7b731
inf2    = f'\x1b[38;2;247;183;49m'
binf    = f'\033[48;2;75;123;236m\x1b[38;2;0;0;0m'      #Info color    - blue    -   #4b7bec
binf2   = f'\033[38;2;75;123;236m'
oinf    = f'\033[48;2;250;130;49m\x1b[38;2;0;0;0m'      #Info color    - orange  -   #fa8231
oinf2   = f'\033[38;2;250;130;49m'
ginf2   = f'\033[38;2;165;177;194m'                      #Info color     - gray   -   #a5b1c2
vinf    = f'\033[48;2;165;94;234m\x1b[38;2;0;0;0m'      #Info color     - violet -   #a55eea
vinf2   = f'\033[38;2;165;94;234m'
bld     = f'\033[1m'
bld2    = f'\x1b[22m'
uln     = f'\x1b[4m'
inv     = f'\033[7m'
inv2    = f'\033[27m'
rs      = f'\x1b[0m'
clscr = "\033[2J"

kfn_tag = f"{inf} Keyframe Nudge Addon: {rs}\n"

def this_spot():
    """
    Use this for easily tracking print statements and where they are called from when debuging objects
    :return: Returns the following string:
            <filename>.py
                └─<line number> ... <class name> -> <function name>.
    """

    info = inspect.stack()
    filename = info[1].filename.split('\\')[-1]

    line_number = info[1][0].f_lineno
    class_name = info[1][0].f_locals["self"].__class__.__name__ if "self" in info[1][0].f_locals.keys() else None
    function_name = info[1][0].f_code.co_name

    return f"{binf}{bld} {filename} {rs}\n\t{binf2}└─{line_number}...{class_name if class_name else '__main__'}->{function_name}(){rs}"


def print_dict_as_table(input: dict):
    name_of_dict = [name for name, value in globals().items() if value == input]
    keys = list(input.keys())
    temp_values = input.values()
    values = []
    for value in temp_values:
        if type(value) == float:
            val_item = f'{value:.3f}'
            values.append(val_item)
        else:
            values.append(str(value))
    print_lines = len(keys)
    
    print_buffer = ''
    
    keys_size = 0
    for key in keys:
        key_len = len(key)
        if keys_size < key_len:
            keys_size = key_len
        else:
            pass
    
    value_size = 0
    for value in values:
        value_len = len(value)
        if value_size < value_len:
            value_size = value_len
        else:
            continue
    line_length = keys_size + value_size + 4
    first_line = f"{binf}┌{f'{name_of_dict}':─^{line_length}}┐{rs}\n"
    print_buffer += first_line
    
    for i in range(print_lines):
        key_value_line = f"{binf}│ {keys[i]:-<{keys_size}}►{inf}•{values[i]:.>{value_size}} {binf}│{rs}\n"
        print_buffer += key_value_line
    last_line = f"{binf}└{'':─^{line_length}}┘{rs}\n"
    print_buffer += last_line
    print(print_buffer)


