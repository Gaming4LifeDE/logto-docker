#!/usr/bin/env python3

import subprocess
import pkg_resources
import argparse
import sys
import secrets
import os

for package in ["jinja2", "rich", "validators"]:
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from jinja2 import Template
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt, Confirm
import validators

with open("templates/docker-compose.override.yml.j2") as template_file:
    template = Template(template_file.read(), trim_blocks=True, lstrip_blocks=True)

parser = argparse.ArgumentParser(prog=__file__, description="Generate your docker-compose.override.yml for Logto")

parser.add_argument("-e", "--endpoint-url", required=True, help="URL for the \"default\" authentication endpoint")
parser.add_argument("-a", "--admin-endpoint-url", required=True, help="URL for the administration endpoint")
parser.add_argument("-p", "--endpoint-port", type=int, default=3001, help="Port where the \"default\" authentication endpoint should be exposed to\nThe port also needs to be included in the URL if Logto will only be reachable there\nDefault: 3001")
parser.add_argument("-P", "--admin-endpoint-port", type=int, default=3002, help="Port where the administration endpoint should be exposed to\nThe port also needs to be included in the URL if Logto will only be reachable there\nDefault: 3002")
# to be implemented
#parser.add_argument("-d", "--postgres-data-dir", default=None, help="Path to the directory where Postgres should store it\'s data.\nDefault: Docker volume default")
parser.add_argument("-o", "--output-file", default="./docker-compose.yml", help="Path where the docker-compose.yml should be saved at")

data = {}
if len(sys.argv) > 1:
    args = parser.parse_args()

# dict for templating data
    # Populate data from args into "data" for templating
    for k, v in vars(args).items():
        data[k] = v
else:
    console = Console()
    intro = Markdown("# Welcome to Logto!\n\n This script will help you generate a docker-compose override file to get started. For this, a few questions will be asked.  \nLet\'s get started!")
    console.print(intro)
    console.line(2)
    while not data.get("endpoint_url"):
        prompt_input = Prompt.ask(prompt="[yellow]Where should Logto be reachable at? [/][magenta]\[eg. https://sso.example.com][/]", console=console)
        if validators.url(prompt_input):
            data["endpoint_url"] = prompt_input
        else:
            print("[red]This URL does not seem to be valid, please try again")
    while not data.get("admin_endpoint_url"):
        prompt_input = Prompt.ask(prompt="[yellow]Where should the Logto administration interface be reachable at? [/][magenta]\[eg. https://sso-admin.example.com][/]", console=console)
        if validators.url(prompt_input):
            data["admin_endpoint_url"] = prompt_input
        else:
            print("[red]This URL does not seem to be valid, please try again")
    while not data.get("endpoint_port"):
        prompt_input = IntPrompt.ask(prompt="[yellow]Which port should Logto be exposed on? [/][magenta]\[1-65536][/]", console=console, default=3001)
        print(prompt_input)
        if prompt_input > 0 and prompt_input < 65536:
            data["endpoint_port"] = prompt_input
        else:
            print("[red]This port does not seem to be valid, please enter a port number between 1 and 65536")
    while not data.get("admin_endpoint_port"):
        prompt_input = IntPrompt.ask(prompt="[yellow]Which port should the admin interface be exposed on? [/][magenta]\[1-65536][/]", console=console, default=3002)
        if prompt_input == data["endpoint_port"]:
            print("[red]The admin endpoint port can not be the same as the main Logto Port!")
        elif prompt_input > 0 and prompt_input < 65536:
            data["admin_endpoint_port"] = prompt_input
        else:
            print("[red]This port does not seem to be valid, please enter a port number between 1 and 65536")
    while not data.get("output_file"):
        prompt_input = Prompt.ask(prompt="[yellow]Where do you want your docker-compose.yml to be saved at? [/]", console=console, default="./docker-compose.yml")
        if (not os.access(os.path.expanduser(prompt_input), os.F_OK) and os.access(os.path.expanduser(os.path.dirname(prompt_input)), os.W_OK)):
            data["output_file"] = prompt_input
        elif os.access(os.path.expanduser(prompt_input), os.F_OK) and os.access(os.path.expanduser(prompt_input), os.W_OK):
            overwrite_confirm = Confirm.ask("[yellow]The specified file exists. Overwrite? [/]", console=console)
            if overwrite_confirm:
                data["output_file"] = prompt_input
            else:
                print("Aborting!")
                sys.exit(1)
        else:
            print("[red]The specified path does not seem to be writable, please try again")

data["postgres_password"] = secrets.token_hex(32)
print(template.render(data))
