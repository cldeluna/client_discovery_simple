#!/usr/bin/python -tt
# Project: client_discovery_simple
# Filename: get_showcmds.py
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/20/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import netmiko
import datetime
import yaml
import os
import re
import dotenv
import getpass


def read_yaml(filename):
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def open_file(filename, mode="r", encoding="utf-8", debug=False):

    """

    General Utility to safely open a file.

    encoding="utf-8"

    :param filename:  file to open
    :param mode: mode in which to open file, defaults to read
    :return:  file handle

    """

    if debug: print(f"in open_file function in cat_config_utils module with filename {filename} and mode as {mode}")

    file_handle = ''
    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode, encoding=encoding, errors='ignore')

    except IOError:
        print("IOError" + str(IOError))
        print(f"open_file() function could not open file with mode {mode} in given path {path}"
              f"\nPlease make sure all result files are closed!")

    return file_handle


def sub_dir(output_subdir, debug=False):
    # Create target Directory if does not exist
    if not os.path.exists(output_subdir):
        os.mkdir(output_subdir)
        print("Directory ", output_subdir, " Created ")
    else:
        if debug:
            print("Directory ", output_subdir, " Already Exists")


def conn_and_get_output(dev_dict, cmd_list, debug=False):

    response = ""
    try:
        net_connect = netmiko.ConnectHandler(**dev_dict)
    except (netmiko.ssh_exception.NetmikoTimeoutException, netmiko.ssh_exception.NetMikoAuthenticationException):
        print(f"Cannot connect to device {dev_dict['ip']}.")

    for cmd in cmd_list:
        if debug:
            print(f"--- Show Command: {cmd}")
        try:
            output = net_connect.send_command(cmd.strip())
            response += f"\n!--- {cmd} \n{output}"
        except Exception as e:
            print(f"Cannot execute command {cmd} on device {dev_dict['ip']}.")
            # continue

    return response


def write_txt(filename, data):
    with open(filename, "w") as f:
        f.write(data)
    return f


def main():
    """
    Basic Netmiko script showing how to connect to a device and save the output.

    """

    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=False)

    fn = "show_cmds.yml"
    cmd_dict = read_yaml(fn)

    # Read in device_file.txt (one ip or fqdn per line)
    fh = open("device_file.txt")

    device_list = []
    if fh:
        devlist = fh.readlines()
        for line in devlist:
            if re.search(r"\w+", line):
                device_list.append(line.strip())

    # SAVING OUTPUT
    output_dir = "local"
    sub_dir(output_dir)

    # User has account without MFA
    usr = os.environ["NET_USR"]
    pwd = os.environ["NET_PWD"]
    sec = os.environ["NET_PWD"]
    mfa = pwd
    sec = pwd

    for dev in device_list:
        devdict = {
            "device_type": arguments.device_type,
            "ip": dev,
            "username": usr,
            "password": mfa,
            "secret": sec,
            "port": arguments.port,
        }

        # RAW Parsing with Python
        print(f"\n===============  Device {dev} ===============")

        # Set the Show Commands to execute by device type or command provided via CLI
        if devdict["device_type"] in ["cisco_ios", "cisco_nxos", "cisco_wlc"]:
            if re.search("ios", devdict["device_type"]):
                cmds = cmd_dict["ios_show_commands"]
            elif re.search("nxos", devdict["device_type"]):
                cmds = cmd_dict["nxos_show_commands"]
            elif re.search("wlc", devdict["device_type"]):
                cmds = cmd_dict["wlc_show_commands"]
            else:
                cmds = cmd_dict["general_show_commands"]
            resp = conn_and_get_output(devdict, cmds, debug=True)

            # Filename
            basefn = f"{dev}_{datestamp}.txt"

            output_dir = os.path.join(os.getcwd(), output_dir, basefn)
            write_txt(output_dir, resp)

            print(f"\nSaving show command output to {output_dir}\n\n")

        else:
            print(f"\n\n\txxx Skip Device {dev} Type {devdict['device_type']}")


# Standard call to the main() function.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script Description",
        epilog="Usage: ' python get_showcmds.py' ",
    )

    # parser.add_argument(
    #     "-d",
    #     "--device",
    #     help="Get show commands from this device (ip or FQDN) and save to file",
    #     action="store",
    #     default="",
    # )
    parser.add_argument(
        "-t",
        "--device_type",
        help="Device Types include cisco_nxos, cisco_asa, cisco_wlc Default: cisco_ios",
        action="store",
        default="cisco_ios",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port for ssh connection. Default: 22",
        action="store",
        default="22",
    )
    # parser.add_argument(
    #     "-o",
    #     "--output_subdir",
    #     help="Name of output subdirectory for show command files",
    #     action="store",
    #     default="local",
    # )
    # parser.add_argument(
    #     "-s", "--show_cmd", help="Execute a single show command", action="store"
    # )
    # parser.add_argument(
    #     "-n",
    #     "--note",
    #     action="store",
    #     help="Short note to distinguish show commands. Ex. -pre or -post",
    # )
    # parser.add_argument(
    #     "-m",
    #     "--mfa",
    #     action="store_true",
    #     help="Multi Factor Authentication will prompt for VIP, MS Auth, Google auth, or other 2-Factor code",
    #     default=False,
    # )
    # parser.add_argument(
    #     "-c",
    #     "--credentials",
    #     action="store_true",
    #     help="Set Credentials via Command Line interactively",
    #     default="",
    # )
    # parser.add_argument(
    #     "-f",
    #     "--file_of_devs",
    #     action="store",
    #     help="Provide the full path to a text file containing an IP or FQDN on each line (see example_device_file.txt) "
    #     "to execute show commands on multiple devices with the same credentials.",
    #     default="",
    # )
    arguments = parser.parse_args()
    main()
