# To save time on declaring often used imports
from re import sub
from .debug_utils import *

def add_external_modules():
    import sys, site, subprocess ,pkg_resources, json
    print(f"{kfn_tag}{'':^2}{inf2}├─ Checking for required modules »» {rs}")
    required_modules = {"pywin32"} #For debug only
    installed_modules = {pkg.key for pkg in pkg_resources.working_set}
    missing_modules = required_modules - installed_modules

    if missing_modules:
        add_path = site.USER_SITE

        if add_path not in sys.path:
            sys.path.append(add_path)

        bpyexe = sys.executable

        try:
            subprocess.call([bpyexe,"-m","ensurepip", '--upgrade'], stdout=subprocess.DEVNULL)
        except:
            pass


        pip_cmd = ['-m', 'pip']
        buffer = subprocess.run([bpyexe, *pip_cmd, 'list', '--outdated', '--format', 'json'],capture_output=True).stdout

        outdated_modules = json.loads(buffer[:-2])
        for module in outdated_modules:
            if module['name'] == 'pip':
                print(f'{err} ! Pip Module is outdated ! {rs}\n{"":^2}{inf2}└─{rs}{inf} Updating... {rs}')
                return_code = subprocess.check_call([bpyexe, *pip_cmd, 'install', '--upgrade', 'pip'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            else:pass



        for module in missing_modules:
            print(f"{'':^2}{err2}└─{rs}{err} ! Module {inv} {module} {inv} not available in blender's python env. ! {rs}\n{'':^2}{inf2}│{'':^2}├─{rs}{inf} Adding... {rs}")
            result = subprocess.check_call([bpyexe, "-m", "pip", "install", module],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if result == 0:
                print(f'{"":^2}{succ2}│{rs}{"":^2}{succ2}└─{rs}{succ} Module {module} Successfully Added.{rs}')
        
        print(f"{'':^2}{succ2}└─{rs}{succ} All required modules are installed {rs}")
        
    else:
        print(f"{'':^2}{succ2}└─{rs}{succ} All required modules are available {rs}")


# import modules guaranteed by blender's python env
import numpy as np

# Safeguard for required modules
print('\n') # separate from prior module outputs
add_external_modules()

# set Numpy print settings
np.set_printoptions(precision=4)

# set Console colors for debug
def set_console_colors():
    import win32console 
    
    handle = win32console.GetStdHandle(-11)
    duplicate = win32console.PyConsoleScreenBufferType(handle)
    mode = duplicate.GetConsoleMode()
    # print(f"{binf}Retrieved Mode is {mode} {rs}{binf2}\uE0B0  {rs}")
    mode |= 4
    duplicate.SetConsoleMode(mode)
    win32console.SetConsoleCP(65001)
    win32console.SetConsoleOutputCP(65001)
    # mode = duplicate.GetConsoleMode()
    # print(f"{binf2}  ├→ │▌{rs}{binf} Retrieved Mode is {mode} {rs}{binf2}\uE0B0  {mode:08b}  \ue0b2{rs}{binf}  {rs} ⮏")
    
set_console_colors()

# Makesure Info output is separate from later modules
print('\n')
