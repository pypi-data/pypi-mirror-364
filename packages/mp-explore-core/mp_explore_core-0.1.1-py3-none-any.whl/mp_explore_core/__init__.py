# SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
import logging
import inspect

from abc import ABC, abstractmethod
from typing import TypedDict, NotRequired, Literal, Any

class ModuleArgument(TypedDict):
    codename: str
    name: str
    description: str
    required: bool
    arg_type: Literal["number", "string", "boolean"]
    default: Any

    @staticmethod
    def list_from_init(func):
        raw_args = list(map(
            lambda x: list(x.split(":"))[1:],
            filter(
                lambda x: x.startswith(":"),
                map(
                    str.strip,
                    func.__doc__.splitlines()
                )
            ),
        ))

        arg_specs = inspect.getfullargspec(func)
        args = list()
        for raw_arg in raw_args:
            if raw_arg[0].split(" ")[0].strip() != "param":
                continue
            
            param_type = raw_arg[0].split(" ")[1]
            param_codename = raw_arg[0].split(" ")[2]

            description = ":".join(raw_arg[1:]).strip()
            if description.startswith("("):
                splitted = description.split("(")[1:]
                param_name = splitted[0].split(")")[0:][0].replace(")", "").strip()
                description = splitted[0].split(")")[1:][0].replace(")", "").strip()
            else:
                param_name = param_codename.replace("_", " ").capitalize()

            args.append({
                "codename": param_codename,
                "name": param_name,
                "description": description,
                "arg_type": param_type,
                "required": (arg_specs.kwonlydefaults or dict()).get(param_codename) is None,
                "default": (arg_specs.kwonlydefaults or dict()).get(param_codename),
            })

        return args

class ModuleDescription(TypedDict):
    description: str

    @staticmethod
    def from_init(func):
        return { 
            "description": "\n".join(list(filter(
                lambda x: x.startswith(":") is False,
                map(
                    str.strip,
                    func.__doc__.splitlines()
                ),
            ))).strip()
        }

class ModuleMaintainer(TypedDict):
    name: str
    description: NotRequired[str]
    email: str

class ModuleDefinition(TypedDict):
    name: str
    identifier: str
    description: ModuleDescription
    maintainers: list[ModuleMaintainer]
    arguments: list[ModuleArgument]

class DataSource(ABC):
    @staticmethod
    @abstractmethod
    def metadata() -> ModuleDefinition:
        pass

    @abstractmethod
    async def fetch_data(self, logger: logging.Logger) -> pd.DataFrame:
        pass

class PipelineProcess(ABC):
    @staticmethod
    @abstractmethod
    def metadata() -> ModuleDefinition:
        pass

    @abstractmethod
    async def pipeline(self, logger: logging.Logger, identifier: str, data: pd.DataFrame) -> pd.DataFrame:
        pass

class DataConsumer(ABC):
    @staticmethod
    @abstractmethod
    def metadata() -> ModuleDefinition:
        pass

    @abstractmethod
    async def consume(self, logger: logging.Logger, data: pd.DataFrame) -> None:
        pass

class Pipeline:
    def __init__(self, sources: list[DataSource], processes: list[PipelineProcess], consumers: list[DataConsumer]):
        self.sources = sources
        self.processes = processes
        self.consumers = consumers
    
    async def run(self, log_level: str):
        logger = logging.getLogger("pipeline")
        logger.setLevel(level=logging.getLevelName(log_level))
        dataset = dict()

        # == RUN SOURCES
        for source in self.sources:
            source_ident = source.metadata()["identifier"]
            logger.debug(f"running source '{source_ident}'")

            source_logger = logging.getLogger("source:" + source_ident)
            source_logger.setLevel(level=log_level)
            dataset[source_ident] = await source.fetch_data(source_logger)

            logger.debug(f"finished running source '{source_ident}'")

        
        # == INCORPORATE METADATA TO FRAMES
        for ident, data in dataset.items():
            dataset[ident] = data.assign(**{
                "__mp_explore__source_identifier": ident,
            })
            
        # == RUN PIPELINE PROCESSES
        logger.debug("finished running sources")
        for ident, data in dataset.items():
            logger.debug(f"starting pipeline for '{ident}'")
            for process in self.processes:
                process_ident = process.metadata()["identifier"]
                logger.debug(f"running process '{process_ident}'")

                process_logger = logging.getLogger("process:" + process_ident)
                process_logger.setLevel(level=log_level)
                value = await process.pipeline(process_logger, ident, data)
                if value is None:
                    logger.warn(f"process '{process_ident}' did not return anything")
                else:
                    dataset[ident] = value

                logger.debug(f"finished running process '{process_ident}'")
        
        # == MERGE DATASET
        logger.debug("finished running processes")
        data = pd.concat(dataset.values(), ignore_index=True)

        # == RUN CONSUMERS
        for consumer in self.consumers:
            consumer_ident = consumer.metadata()["identifier"]
            logger.debug(f"running consumer '{consumer_ident}'")

            consumer_logger = logging.getLogger("consumer:" + consumer_ident)
            consumer_logger.setLevel(level=log_level)
            await consumer.consume(consumer_logger, data)

            logger.debug(f"finished running consumer '{consumer_ident}'")
        
