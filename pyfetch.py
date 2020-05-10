from subprocess import Popen, PIPE, DEVNULL
from os import environ
from os.path import isfile, exists
from shutil import which
import time

def run_command(command):
    process = Popen(command, stdout=PIPE, universal_newlines=True, shell=True,stderr=DEVNULL)
    stdout, stderr = process.communicate()
    del stderr
    return stdout

def os_name():
    if isfile('/bedrock/etc/os-release'):
        os_file = '/bedrock/etc/os-release'
    elif isfile('/etc/os-release'):
        os_file = '/etc/os-release'


    pretty_name = run_command(("cat "+os_file+" | grep 'PRETTY_NAME'")).replace("PRETTY_NAME=", "").replace('''"''', "")
    return pretty_name


def model_info():
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
            product_info = str(product_info+" "+line)
    return product_info


def misc_func():
    shell_name = environ["SHELL"].split('/')[-1]
    shell_ver = ""
    if shell_name == "fish":
        shell_ver = run_command("fish --version").replace("fish, version ","")
    elif shell_name == "bash":
        shell_ver = environ['BASH_VERSION'].split('(')[0]
    if shell_ver != "":
        shell = str(shell_name+" shell_ver")
    else:
        shell = shell_name
    
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


def pac_msg_madness():
    pac_msg = "Packages:"
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


#cpu stuff

def fetch_cpu_info():
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
    del cpu_freq_info, cpu_count, cpu_info, cpu_max_freq_mhz, cpu_max_freq_ghz
    return full_cpu_info


def non_debug():
    pac_msg = pac_msg_madness()
    full_cpu_info = fetch_cpu_info()
    product_info = model_info()
    pretty_name = os_name()
    shell, resolution, terminal_emu, kernel, uptime = misc_func()
    return pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime

def debug():
    global pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime

    total_time = 0
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

def display():
    pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime = non_debug()
    print(f'OS: {pretty_name}'.rstrip('\n'))
    print(f'Host: {product_info}'.rstrip('\n'))
    print(f'Kernel: {kernel}'.rstrip('\n'))
    print(f'Uptime: {uptime}'.rstrip('\n'))

    if pac_msg != "Packages:":
        print(pac_msg.rstrip('\n'))

    if shell != "":
        print(f'Shell: {shell}')

    if resolution != "":
        print(f'Resolution: {resolution}')

    print(f'DE: ')
    print(f'WM: ')
    print(f'WM Theme: ')
    print(f'Theme: ')
    print(f'Icons: ')
    if terminal_emu != "":
        print(f'Terminal: {terminal_emu}')
    print(f'CPU: {full_cpu_info}')
    print(f'GPU: ')
    print(f'Memory: ')

display()