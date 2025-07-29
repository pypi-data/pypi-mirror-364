# SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import tomllib
import importlib
import inspect
import asyncio
import logging

from mp_explore_core import Pipeline, DataSource, PipelineProcess, DataConsumer

class Workflow:
    def __init__(self, workflow, on_module_not_found, log_level="INFO"):
        importlib.invalidate_caches()

        self.on_module_not_found = on_module_not_found
        self.logger = logging.getLogger("mp-explore-cli")
        self.logger.setLevel(logging.getLevelName(log_level))
        with open(workflow, "rb") as f:
            self.workflow = tomllib.load(f)
    
    def sources(self):
        sources = list()
        for source_id in self.workflow["workflow"]["sources"]:
            source = self.workflow["sources"][source_id]
            try:
                module = importlib.import_module(source["module"])
            except ImportError as e:
                if self.on_module_not_found is not None:
                    self.on_module_not_found(source["module"])
                    module = importlib.import_module(source["module"])
                else:
                    raise e

            classes = list()
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, DataSource) and not inspect.isabstract(obj):
                    classes.append((name, obj))
            
            if len(classes) > 1:
                self.logger.warn(f"Multiple source classes for source '{source_id}' were found, using '{classes[0][0]}'")
            elif len(classes) == 0:
                raise Exception(f"No sources classes found for source '{source_id}'")
            
            del source["module"]
            sources.append(classes[0][1](**source))

        return sources

    def processes(self):
        processes = list()
        for process_id in self.workflow["workflow"]["processes"]:
            process = self.workflow["processes"][process_id]
            try:
                module = importlib.import_module(process["module"])
            except ImportError as e:
                if self.on_module_not_found is not None:
                    self.on_module_not_found(process["module"])
                    module = importlib.import_module(process["module"])
                else:
                    raise e

            classes = list()
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PipelineProcess) and not inspect.isabstract(obj):
                    classes.append((name, obj))
            
            if len(classes) > 1:
                self.logger.warn(f"Multiple process classes for process '{process_id}' were found, using '{classes[0][0]}'")
            elif len(classes) == 0:
                raise Exception(f"No process classes were found for process '{process_id}'")
            
            del process["module"]
            processes.append(classes[0][1](**process))
        
        return processes
    
    def consumers(self):
        consumers = list()
        for consumer_id in self.workflow["workflow"]["consumers"]:
            consumer = self.workflow["consumers"][consumer_id]
            try:
                module = importlib.import_module(consumer["module"])
            except ImportError as e:
                if self.on_module_not_found is not None:
                    self.on_module_not_found(consumer["module"])
                    module = importlib.import_module(consumer["module"])
                else:
                    raise e

            classes = list()
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, DataConsumer) and not inspect.isabstract(obj):
                    classes.append((name, obj))
            
            if len(classes) > 1:
                self.logger.warn(f"Multiple consumer classes for source '{consumer_id}' were found, using '{classes[0][0]}'")
            elif len(classes) == 0:
                raise Exception(f"No consumer classes were found for source '{consumer_id}'")
            
            del consumer["module"]
            consumers.append(classes[0][1](**consumer))
        
        return consumers
    
    def run_workflow(self, log_level: str):
        sources = self.sources()
        processes = self.processes()
        consumers = self.consumers()

        pipeline = Pipeline(sources=sources, processes=processes, consumers=consumers)
        asyncio.run(pipeline.run(log_level=log_level.upper() if log_level is not None else "INFO"))
