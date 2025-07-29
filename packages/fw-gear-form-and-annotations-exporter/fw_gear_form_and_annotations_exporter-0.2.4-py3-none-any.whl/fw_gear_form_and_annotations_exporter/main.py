"""Main module."""

import datetime
import logging

import pandas as pd
from fw_client import FWClient
from fw_gear import GearContext

from .collect_form_annot_data import (
    build_annotations_dataframe,
    build_annotations_list,
    build_form_responses_dataframe,
    build_form_responses_list,
    process_task_list,
)
from .flywheel_api_helpers import get_project_tasks, get_protocol_from_name

log = logging.getLogger(__name__)


def run(  # noqa: PLR0913
    context: GearContext,
    api_key: str,
    protocol_name: str,
    annotations_scope: str,
    form_responses_scope: str,
    read_timeout: int,
):
    """Run the algorithm defined in this gear.

    Args:
        context (GearContext): The gear context.
        api_key (str): The API key generated for this gear run.
        protocol_name (str): The name of the protocol to use.
        annotations_scope (str): The scope of the annotations to export (task, non-task,
                                 both, or none).
        form_responses_scope (str): The scope of the form responses to export (task or
                                    none).
        read_timeout (int): The read timeout for the API requests. Defaults to 60.

    Returns:
        int: The exit code.
    """
    client = FWClient(api_key=api_key, timeout=read_timeout)

    # Ensure the protocol is defined for the project of the analysis container
    destination_container = context.client.get(context.config.destination["id"])
    # get parent type and id
    dest_parent_type = destination_container.parent["type"]
    dest_parent_id = destination_container.parent["id"]
    dest_proj_id = destination_container.parents["project"]
    if protocol_name:
        # Ensure the protocol exists for that project
        # Protocol Names are unique within a project
        if not (
            protocol := get_protocol_from_name(
                client, protocol_name=protocol_name, project_id=dest_proj_id
            )
        ):
            log.error(
                "Protocol %s not found for project (%s).", protocol_name, dest_proj_id
            )
            log.info(
                "Check protocol definitions and project permissions for your API key."
            )
            return 1

        project_id = dest_proj_id
        form_id = protocol["form_id"]

        tasks = get_project_tasks(
            client, project_id, protocol["_id"], dest_parent_type, dest_parent_id
        )

    else:
        project_id = None
        form_id = None
        tasks = {"results": []}

    tasks_df = process_task_list(client, tasks["results"], protocol_name)

    # TODO: We may want to restrict the responses and annotations to the container
    #       in which the analysis gear is run. Currently it is based on the project.

    # If the form_responses_scope is assigned and a protocol_is found, else skip
    form_responses_df = pd.DataFrame()
    if form_responses_scope and form_id:
        form_responses = build_form_responses_list(
            client, form_id, form_responses_scope, dest_parent_type, dest_parent_id
        )

        form_responses_df = build_form_responses_dataframe(tasks_df, form_responses)
    # TODO: Take into account if the various indicators are not present...

    # If the annotations_scope is assigned, else skip
    annotation_values_df = pd.DataFrame()
    if annotations_scope:
        annotations_list, files_df = build_annotations_list(
            client, tasks_df, annotations_scope, dest_parent_type, dest_parent_id
        )

        annotation_values_df = build_annotations_dataframe(
            tasks_df, files_df, annotations_list
        )

    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")

    # The first csv file is a list of all the form_responses, including blanks
    # for missing responses incomplete tasks
    if not form_responses_df.empty:
        log.info("Exporting form responses to CSV file.")
        output_filename = f"form-responses-{formatted_date}.csv"
        form_responses_df.to_csv(context.output_dir / output_filename, index=False)

    # The second csv file is a list of all the annotations, some which are
    # associated with Tasks... and some which are not.
    if not annotation_values_df.empty:
        log.info("Exporting annotations to CSV file.")
        output_filename = f"annotations-{formatted_date}.csv"
        annotation_values_df.to_csv(context.output_dir / output_filename, index=False)

    return 0
