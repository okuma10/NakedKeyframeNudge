# To save time on declaring often used imports
from re import sub
from .debug_utils import *

def add_external_modules():
    import sys, site, subprocess ,pkg_resources, json
    print(f"{kfn_tag}{'':^2}{inf2}├─ Checking for required modules »» {rs}")
    required_modules = {"pywin32"} #For debug only
    installed_modules = {pkg.key for pkg in pkg_resources.working_set} # Getting sets of module names
    missing_modules = required_modules - installed_modules # Removing names from the required modules (using set substraction)

    if missing_modules: # if there are any missing modules left
    # ╭─────── Adding the local python site-packages path? What for? ─────╮
        add_path = site.USER_SITE

        if add_path not in sys.path:
            sys.path.append(add_path)
    # ╰────────────────────── maybe I don't need this? ──────────────────────╯

        # Get Blender's Python Venv path.'
        bpyexe = sys.executable
        # print(f"Blender executable? {bpyexe}")
        try:
            subprocess.call([bpyexe,"-m","ensurepip", '--upgrade'], stdout=subprocess.DEVNULL)
        except:
            pass

        # Check for outdated modules in Blender's Python Venv'
        pip_cmd = ['-m', 'pip']
        buffer = subprocess.run([bpyexe, *pip_cmd, 'list', '--outdated', '--format', 'json'],capture_output=True).stdout
        
        # Check if pip is inside the outdated modules
        outdated_modules = json.loads(buffer[:-2])
        for module in outdated_modules:
            if module['name'] == 'pip':
                print(f'{err} ! Pip Module is outdated ! {rs}\n{"":^2}{inf2}└─{rs}{inf} Updating... {rs}')
                return_code = subprocess.check_call([bpyexe, *pip_cmd, 'install', '--upgrade', 'pip','--user'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            else:pass


        # for the modules that are missing try installing them
        for module in missing_modules:
            result = -1; # debugging
            print(f"{'':^2}{err2}└─{rs}{err} ! Module {inv} {module} {inv} not available in blender's python env. ! {rs}\n{'':^2}{inf2}│{'':^2}├─{rs}{inf} Adding... {rs}")
            # Set site-packages path
            site_pck_fp = "-t " + "\\".join(bpyexe.split('\\')[:-2]) + "\\lib\\site-packages"
            # Compile Command
            command = f"'{bpyexe} -m pip install {module} {site_pck_fp}'"
            # Make Platform specific since on windows we can use powershell
            if sys.platform.startswith("win"):
                # result = subprocess.check_call([bpyexe, "-m", "pip", "install", module, '--user'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                result = subprocess.run(
                                [   "powershell", "Invoke-Expression","-Command", 
                                    command],
                                    shell=True
                )
            elif sys.platfrom.startswith("linux"):
                print(f"LINUX: TODO!")

            # Evaluate the return result code ...for Debugging mainly
            if result.returncode == 0:
                print(f'{"":^2}{succ2}│{rs}{"":^2}{succ2}└─{rs}{succ} Module {module} Successfully Added.{rs}')
            else:
                print(f'{"":^2}{err2}│{rs}{"":^2}{err2}└─{rs}{err} Module {module} Failed Installation.{rs}\n{result.stdout}')


        
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
