#!/usr/bin/env python3

import pkg_resources
import argparse
import sys
import secrets

for package in ["jinja2", "rich"]:
    try:
        pkg_resources.get_distribution("jinja2")
    except pkg_resources.DistributionNotFound:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from jinja2 import Template
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

with open("templates/docker-compose.override.yml.j2") as template_file:
    template = Template(template_file.read(), trim_blocks=True, lstrip_blocks=True)

parser = argparse.ArgumentParser(prog=__file__, description="Generate your docker-compose.override.yml for Logto")

parser.add_argument("-e", "--endpoint-url", help="URL for the \"default\" authentication endpoint")
parser.add_argument("-a", "--admin-endpoint-url", help="URL for the administration endpoint")
parser.add_argument("-p", "--endpoint-port", type=int, default=3001, help="Port where the \"default\" authentication endpoint should be exposed to\nThe port also needs to be included in the URL if Logto will only be reachable there\nDefault: 3001")
parser.add_argument("-P", "--admin-endpoint-port", type=int, default=3002, help="Port where the administration endpoint should be exposed to\nThe port also needs to be included in the URL if Logto will only be reachable there\nDefault: 3002")
parser.add_argument("-d", "--postgres-data-dir", default=None, help="Path to the directory where Postgres should store it\'s data.\nDefault: Docker volume default")
args = parser.parse_args()

# dict for templating data
data = {}
if len(sys.argv) > 1:
    # Populate data from args into "data" for templating
    for k, v in vars(args).items():
        data[k] = v
else:
    console = Console()
    intro = Markdown("# Welcome to Logto!\n\n This script will help you generate a docker-compose override file to get started. For this, a few questions will be asked.  \nLet\'s get started!")
    console.print(intro)
    console.line(2)
    data["endpoint_url"] = Prompt.ask(prompt="[yellow]Where should Logto be reachable at? [/][magenta]\[eg. https://sso.example.com\][/]", console=console)
    data["admin_endpoint_url"] = Prompt.ask(prompt="[yellow]Where should the Logto administration interface be reachable at? [/][magenta]\[eg. https://sso-admin.example.com\][/]", console=console)
    data["endpoint_port"] = IntPrompt.ask(prompt="[yellow]Which port should Logto be exposed on?", console=console, default=3001)

print(template.render(data))
