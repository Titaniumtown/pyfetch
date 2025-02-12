from subprocess import Popen, PIPE, DEVNULL
from os import environ
from os.path import isfile, exists
from shutil import which
import time
import sys
from logos import logo_array, bcolors

def run_command(command):
    process = Popen(command, stdout=PIPE, universal_newlines=True, shell=True,stderr=DEVNULL)
    stdout, stderr = process.communicate()
    del stderr
    return stdout

def battery_info():
    if sys.platform == 'darwin':  # Check for macOS
        battery_percentage = run_command("pmset -g batt | grep -Eo '\\d+%' | cut -d% -f1")
        if battery_percentage:
            return f"{battery_percentage}"
    else:  # Assume Linux
        battery_path = "/sys/class/power_supply/BAT0"
        if exists(battery_path):
            with open(f"{battery_path}/capacity", "r") as f:
                battery_percentage = f.read().strip()
            return f"{battery_percentage}"
    return ""

def os_name():
    if isfile('/bedrock/etc/os-release'):
        os_file = '/bedrock/etc/os-release'
    elif isfile('/etc/os-release'):
        os_file = '/etc/os-release'
    elif sys.platform == 'darwin':  # Check for macOS
        pretty_name = run_command("sw_vers -productName").strip() + ' ' + run_command("sw_vers -productVersion").strip()
        return pretty_name
    if isfile('/bedrock/etc/os-release'):
        os_file = '/bedrock/etc/os-release'
    elif isfile('/etc/os-release'):
        os_file = '/etc/os-release'


    pretty_name = run_command(("cat "+os_file+" | grep 'PRETTY_NAME'")).replace("PRETTY_NAME=", "").replace('''"''', "")
    return pretty_name


def model_info():
    if sys.platform == 'darwin':  # Check for macOS
        model_name = run_command("sysctl -n hw.model").strip()
        return model_name
    else:
        product_info = ""
        if exists("/sys/devices/virtual/dmi/id/product_name"):
            with open("/sys/devices/virtual/dmi/id/product_name", "r") as f:
                line = f.read().rstrip('\n')
                product_info = line

        if exists("/sys/devices/virtual/dmi/id/product_version"):
            line = run_command("cat /sys/devices/virtual/dmi/id/product_version").rstrip('\n')
            if product_info == "":
                product_info = line
            else:
                product_info = str(product_info + " " + line)

        return product_info


def misc_func():
    shell_name = environ["SHELL"].split('/')[-1]
    shell_ver = ""
    if shell_name == "fish":
        shell_ver = run_command("fish --version").replace("fish, version ","")
    elif shell_name == "bash":
        shell_ver = environ['BASH_VERSION'].split('(')[0]
    if shell_ver != "":
        shell = str(shell_name+" "+shell_ver).rstrip('\n')
    else:
        shell = shell_name
    
    if sys.platform == 'darwin':  # Check for macOS
        resolution = run_command("system_profiler SPDisplaysDataType | awk '/Resolution:/ {print $2\"x\"$4\" \"}'")
        terminal_emu = run_command("echo $TERM_PROGRAM")
        kernel = run_command("uname -r")
        uptime = run_command("uptime | awk '{print $3\" \"$4\" \"$5}'")
    else:
        resolution = run_command("cat /sys/class/drm/*/modes").split('\n')[0]
        terminal_emu = environ["TERM"]
        kernel = run_command("uname -r")
        uptime = run_command("uptime -p").replace("up ", "")

    
    
    return shell, resolution, terminal_emu, kernel, uptime

def pac_msg_util(input, pac_manager, pac_msg):
    return f'{pac_msg} {str(input)} ({pac_manager})'

def pac_msg_append(command, pac_manager, pac_msg):
    binary = command.split(" ")[0]
    if which(binary) != None:
        num = len(run_command(command).splitlines())
        if num != 0:
            return pac_msg_util(len(run_command(command).splitlines()), pac_manager, pac_msg)
        else:
            return pac_msg
    else:
        return pac_msg

def hostname():
    username = environ['USER']
    hostname = run_command('hostname').rstrip('\n')
    return bcolors.OKGREEN + f'{username}@{hostname}' + bcolors.ENDC

def pac_msg_madness():
    pac_msg = f"Packages:{bcolors.ENDC}"
    if sys.platform == 'darwin':  # Check for macOS
        pac_msg = pac_msg_append("brew list -1", "Homebrew", pac_msg)
    else:
        pac_msg = pac_msg_append("kiss -l", "kiss", pac_msg)
        pac_msg = pac_msg_append("pacman -Qq --color never", "pacman", pac_msg)
        pac_msg = pac_msg_append("dpkg-query -f '.\n' -W", "dpkg", pac_msg)
        pac_msg = pac_msg_append("rpm -qa", "rpm", pac_msg)
        pac_msg = pac_msg_append("xbps-query -l", "xbps", pac_msg)
        pac_msg = pac_msg_append("apk info", "apk", pac_msg)
        pac_msg = pac_msg_append("opkg list-installed", "opkg", pac_msg)
        pac_msg = pac_msg_append("pacman-g2 -Q", "pacman-g2", pac_msg)
        pac_msg = pac_msg_append("lvu installed", "lvu", pac_msg)
        pac_msg = pac_msg_append("tce-status -i", "tce-status", pac_msg)
        pac_msg = pac_msg_append("pkg_info", "pkg_info", pac_msg)
        pac_msg = pac_msg_append("tazpkg list", "tazpkg", pac_msg)
        pac_msg = pac_msg_append("gaze installed", "sorcery", pac_msg)
        pac_msg = pac_msg_append("alps showinstalled", "alps", pac_msg)
        pac_msg = pac_msg_append("butch list", "butch", pac_msg)
        pac_msg = pac_msg_append("mine -q", "mine", pac_msg)
    return pac_msg


def de_info():
    if sys.platform == 'linux':
        de = environ['DESKTOP_SESSION']
        if de.lower() == 'gnome'.lower():
            wm = "Mutter"
        else:
            wm = "Unknown"
        wmtheme, theme, icons = "", "", ""
    
    elif sys.platform == 'darwin':  # Check for macOS
        de = 'Aqua'
        wm = 'Quartz Compositor'
        wmtheme, theme, icons = "", "", ""
    return de, wm, wmtheme, theme, icons

#cpu stuff
def fetch_cpu_info():
    if sys.platform == 'darwin':  # Check for macOS
        cpu_count = int(run_command("sysctl -n hw.ncpu"))
        cpu_info = run_command("sysctl -n machdep.cpu.brand_string")
        cpu_freq_info = run_command("sysctl -n hw.cpufrequency_max").strip()
        full_cpu_info = f'{cpu_info} ({cpu_count}) @ {cpu_freq_info}Hz'
    else:
        cpu_count = len(run_command("ls /sys/class/cpuid/ | sort").split('\n')) - 1
        cpu_info = run_command("cat /proc/cpuinfo | grep 'model name'").split('\n')[0].replace("model name	: ","").replace("Core(TM)","").replace("(R)","").replace("CPU","").replace("  "," ").split('@')[0]
        cpu_max_freq = int(run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"))
        cpu_max_freq_mhz = cpu_max_freq / 1000
        cpu_max_freq_ghz = cpu_max_freq / 1000 / 1000

        if cpu_max_freq_ghz > 1:
            cpu_freq_info = str(str(round(cpu_max_freq_ghz, 3))+"GHz")
        else:
            cpu_freq_info = str(str(round(cpu_max_freq_mhz, 3))+"MHz")

        full_cpu_info = f'{cpu_info}({cpu_count}) @ {cpu_freq_info}'

    return cpu_info

def gpu_info():
    if sys.platform == 'darwin':  # Check for macOS
        gpu_info = run_command("system_profiler SPDisplaysDataType | awk '/Chipset Model:/ {print $3, $4, $5, $6, $7}'")
        return gpu_info.strip()
    else:
        gpu_info = ""
        if exists("/proc/driver/nvidia/version"):
            with open("/proc/driver/nvidia/version", "r") as f:
                gpu_info = f.read().split(',')[0].strip()
        elif exists("/sys/class/dmi/id/product_name"):
            gpu_info = run_command("lspci | grep -i vga").split(':')[2].split('(')[0].strip()

        return gpu_info

def memory_info():
    if sys.platform == 'darwin':  # Check for macOS
        total_memory = run_command("sysctl -n hw.memsize")
        total_memory_gb = round(int(total_memory) / (1024 * 1024 * 1024), 2)
        return f"{total_memory_gb} GB"
    else:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
            total_memory = int(lines[0].split()[1]) // 1024
            free_memory = int(lines[2].split()[1]) // 1024
            used_memory = total_memory - free_memory

        return f"{used_memory} MB / {total_memory} MB"

def non_debug():
    battery = battery_info()
    pac_msg = pac_msg_madness()
    full_cpu_info = fetch_cpu_info()
    product_info = model_info()
    pretty_name = os_name()
    hostname_info = hostname()
    shell, resolution, terminal_emu, kernel, uptime = misc_func()
    gpu = gpu_info()
    memory = memory_info()  # Add this line to retrieve memory information
    return battery, pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime, hostname_info, gpu, memory

def debug():
    global pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime, hostname
    total_time = 0

    start_time = time.time()
    hostname = hostname()
    end_time = time.time()
    hostname_time = end_time - start_time
    total_time += hostname_time
    print("hostname time:",str(round(hostname, 5)))

    start_time = time.time()
    pac_msg = pac_msg_madness()
    end_time = time.time()
    pac_msg_time = end_time - start_time
    total_time += pac_msg_time
    print("pac_msg time:",str(round(pac_msg_time, 5)))

    start_time = time.time()
    full_cpu_info = fetch_cpu_info()
    end_time = time.time()
    cpu_time = end_time - start_time
    total_time += cpu_time
    print("cpu time:",str(round(cpu_time, 5)))

    start_time = time.time()
    product_info = model_info()
    end_time = time.time()
    model_time = end_time - start_time
    total_time += model_time
    print("model_info time:",str(round(model_time, 5)))

    start_time = time.time()
    pretty_name = os_name()
    end_time = time.time()
    os_time = end_time - start_time
    total_time += os_time
    print("os_name time:",str(round(os_time, 5)))

    start_time = time.time()
    shell, resolution, terminal_emu, kernel, uptime = misc_func()
    end_time = time.time()
    misc_func_time = end_time - start_time
    total_time += misc_func_time
    print("Misc function time:",str(round(misc_func_time, 5)))

    print("Total time:",str(round(total_time, 5))+'\n')
# debug()

def dash_gen(num):
    result = ""
    for i in range(num):
        result = str(result+"-")
    return result

def space_gen(num):
    result = ""
    for i in range(num):
        result = str(result+" ")
    return result

def display_array():
    battery, pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime, hostname, gpu, memory = non_debug()
    de, wm, wmtheme, theme, icons = de_info()
    data = []
    if hostname != "":
        data.append(hostname.rstrip('\n'))
        data.append(dash_gen(len(hostname.rstrip('\n'))))
        
    if battery != "":
        data.append(f'{bcolors.YELLOW}Battery{bcolors.ENDC}: {battery}'.rstrip('\n'))

    if pretty_name != "":
        data.append(f'{bcolors.YELLOW}OS{bcolors.ENDC}: {pretty_name}'.rstrip('\n'))
    
    if product_info != "":
        data.append(f'{bcolors.YELLOW}Host{bcolors.ENDC}: {product_info}'.rstrip('\n'))
    
    if kernel != "":
        data.append(f'{bcolors.YELLOW}Kernel{bcolors.ENDC}: {kernel}'.rstrip('\n'))
    
    if uptime != "":
        data.append(f'{bcolors.YELLOW}Uptime{bcolors.ENDC}: {uptime}'.rstrip('\n'))

    if pac_msg != "Packages:":
        data.append(f'{bcolors.YELLOW}{pac_msg}{bcolors.ENDC}'.rstrip('\n'))

    if shell != "":
        data.append(f'{bcolors.YELLOW}Shell{bcolors.ENDC}: {shell}')

    if resolution != "":
        data.append(f'{bcolors.YELLOW}Resolution{bcolors.ENDC}: {resolution}'.rstrip('\n'))
    
    if de != "":
        data.append(f'{bcolors.YELLOW}DE{bcolors.ENDC}: {de}')
    
    if wm != "":
        data.append(f'{bcolors.YELLOW}WM{bcolors.ENDC}: {wm}')
    
    if wmtheme != "":
        data.append(f'WM Theme: {wmtheme}')
    
    if theme != "":
        data.append(f'Theme: {theme}')
    
    if icons != "":
        data.append(f'Icons: {icons}')
    
    if terminal_emu != "":
        data.append(f'{bcolors.YELLOW}Terminal{bcolors.ENDC}: {terminal_emu}'.rstrip('\n'))
    
    if full_cpu_info != "":
        data.append(f'{bcolors.YELLOW}CPU{bcolors.ENDC}: {full_cpu_info}'.rstrip('\n'))
    
    if gpu != "":
        data.append(f'{bcolors.YELLOW}GPU{bcolors.ENDC}: {gpu}')

    if memory != "":
        data.append(f'{bcolors.YELLOW}Memory{bcolors.ENDC}: {memory}')

    #Print terminal color blocks:
    data.append(bcolors.BLACK + "███" + bcolors.RED + "███" + bcolors.OKGREEN + "███" + bcolors.YELLOW + "███" + bcolors.OKBLUE + "███" + bcolors.PINK + "███" + bcolors.OKCYAN + "███" + bcolors.GREY + "███")
    return data



def logo_test():
    if sys.platform == 'darwin':  # Check for macOS
        sel_logo = logo_array[1]  # Select the Mac logo from the logo_array
    else:
        sel_logo = logo_array[0]  # Select the default logo (bedrock_logo) for other systems

    sys_info = display_array()
    max_size = max(len(sel_logo), len(sys_info))
    max_logo_len = max(len(ele) for ele in sel_logo)

    for i in range(max_size):
        if i < len(sel_logo) and i < len(sys_info):
            print(f"{sel_logo[i]:<{max_logo_len}}   {sys_info[i]}")
        elif i < len(sel_logo):
            print(sel_logo[i])
        elif i < len(sys_info):
            print(f"{' ' * max_logo_len}   {sys_info[i]}")


logo_test()