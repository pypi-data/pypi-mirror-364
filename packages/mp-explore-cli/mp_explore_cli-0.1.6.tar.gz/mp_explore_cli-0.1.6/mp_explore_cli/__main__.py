# SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from . import Workflow

from mp_explore_core import Pipeline

import sys
import subprocess
import asyncio
import tomllib
import importlib
import inspect
import logging

import click

logger = logging.getLogger(__name__)

@click.command()
@click.option('--workflow', '-w', required=True)
@click.option('--log-level', '-l', default="INFO")
@click.option('--install-deps', is_flag=True, help='Install dependencies automatically')
def mp_explore(workflow, install_deps, log_level):
    """Run modules in the CLI"""

    workflow = Workflow(workflow, log_level=log_level, on_module_not_found=install_module if install_deps else ask_install_module)

    sources = workflow.sources()   
    logger.info("All sources instantiated")

    processes = workflow.processes()
    logger.info("All processes instantiated")
    
    consumers = workflow.consumers()
    logger.info("All consumers instantiated")

    pipeline = Pipeline(sources=sources, processes=processes, consumers=consumers)
    asyncio.run(pipeline.run(log_level=log_level.upper() if log_level is not None else "INFO"))

    logger.info("Pipeline ran successfully!")

def ask_install_module(mod):
    if click.confirm(f"Module '{mod}' was not found. Would you like to install it now using pip?"):
        install_module(mod)
    else:
        logger.error(f"Cannot proceed without '{mod}', please install it and try again")
        raise Exception(f"Cannot proceed without '{mod}'")

def install_module(mod):
    subprocess.check_call([sys.executable, "-m", "pip", "install", mod])

if __name__ == "__main__":
    mp_explore()