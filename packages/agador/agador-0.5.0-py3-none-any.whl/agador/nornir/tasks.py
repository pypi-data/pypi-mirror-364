import logging
import traceback
from nornir.core.task import Result, Task
from nornir.core.exceptions import NornirSubTaskError
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from umnet_napalm import get_network_driver
import re

from ..utils import get_device_cmd_list
from ..mappers.save_to_file import SaveResult
from ..mappers.save_to_db import ResultsToDb


logger = logging.getLogger(__name__)


def record_failure(result: Result, failure_message: str, e: Exception = None):
    """
    If a failure is detected, want to record a failed result
    with an appropriate message. If an exception was raised want to log that
    as well.
    """
    result.failed = True
    result.result = failure_message
    if e:
        result.exception = str(e) + "\n" + str(traceback.format_exc())


def process_device(
    task: Task,
    cmd_map: dict,
    db_url: str,
) -> Result:
    """
    Run a set of commands against a specific device based on the
    command map.
    """

    device_result = Result(host=task.host, result="Completed sucessfully")
    db_engine = create_engine(db_url)

    # first figure out which commands to run against this host
    cmd_list = get_device_cmd_list(cmd_map, task.host)

    # if no commands match for the host it's not a failure, and we want
    # to return before attempting to connect to the device.
    logger.debug(f"Running getters on {task.host.name}: {cmd_list}")
    if not cmd_list:
        logger.debug(f"No commands to execute for {task.host.name}")
        device_result.result = "No commands to execute"
        return device_result

    # finding that for multiprocessing it's cleaner to use the context
    # manager - by this we mean 'with network_driver as device' - because
    # connection failures that raise exceptions aren't otherwise well tolerated.
    # As a result we're not using the connection plugin and are instead establishing
    # the connection manually.
    try:
        network_driver = get_network_driver(task.host.platform)
    except NotImplementedError as e:
        record_failure(device_result, "Unsupported platform", e)
        return device_result

    parameters = {
        "hostname": task.host.hostname,
        "username": task.host.username,
        "password": task.host.password,
        "optional_args": {},
    }
    parameters.update(task.host.connection_options["umnet_napalm"].extras)

    getter_results = {}
    try:
        with network_driver(**parameters) as device:
            for cmd, getter in cmd_list.items():
                try:
                    method = getattr(device, getter)
                    getter_results[cmd] = method()

                except Exception as e:
                    # panos connection failures show up as 'command' failures
                    if type(e).__name__ == "PanXapiError" and re.search(
                        r"(service not known|Invalid Credential)", str(e)
                    ):
                        record_failure(
                            device_result, "Connection or Authentication Error", e
                        )
                        break
                    record_failure(device_result, f"Error executing {cmd}", e)

    # 'outer' failures are connection failures
    except Exception as e:
        record_failure(device_result, "Connection or Authentication Error", e)

    # for each command save data using the appropriate methods based
    # on the command map
    for cmd, result in getter_results.items():
        if "save_to_db" in cmd_map[cmd]:
            try:
                task.run(
                    name=f"{cmd}_save_to_db",
                    task=update_table,
                    result=result,
                    engine=db_engine,
                    mapper=cmd_map[cmd]["save_to_db"],
                )
            except NornirSubTaskError as e:
                record_failure(device_result, f"error saving {cmd} to db", e)

        if "save_to_file" in cmd_map[cmd]:
            try:
                task.run(
                    name=f"{cmd}_save_to_file",
                    task=save_to_file,
                    result=result,
                    mapper=cmd_map[cmd]["save_to_file"]["mapper"],
                )
            except NornirSubTaskError as e:
                record_failure(device_result, f"error saving {cmd} to file", e)

    return device_result


def update_table(
    task: Task,
    result: Result,
    engine: Engine,
    mapper: ResultsToDb,
) -> Result:
    """
    Generic task for taking the results from a previous "napalm_get"
    task and saving it to the database
    """
    mapper(task.host.name, task.host.hostname, result, engine)

    return Result(host=task.host)


def save_to_file(
    task: Task,
    result: dict,
    mapper: SaveResult,
) -> Result:
    """
    Task for saving to a file
    """
    mapper.write_to_file(task.host, result)

    return Result(host=task.host)
