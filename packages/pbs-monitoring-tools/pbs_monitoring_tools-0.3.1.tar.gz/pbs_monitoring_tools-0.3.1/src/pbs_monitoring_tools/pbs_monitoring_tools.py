import argparse
import logging
import sys
from typing import List
import yaml


from proxmoxer import ProxmoxAPI, ProxmoxResource

from .helpers.helpers import (
    get_all_backups,
    check_full_estimated_date,
    check_backups_status,
    check_last_backups_expiration,
    get_datastores_list,
    print_detailed_errors,
)


def get_cli_parser():
    """
    Parameters list:
    - auth: raise error if you try to use script without authentication data
    """

    parser = argparse.ArgumentParser(description="Proxmox Backup Server tool.")

    parser.add_argument(
        "--auth-file",
        action="store",
        required=True,
        help="YAML file that contains host, username and password to connect to Proxmox server.",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Get proxmox backup monitoring tools version.",
    )

    parser.add_argument(
        "--datastores",
        help="Datastores names for which you want to get status information. If not provided, the tool defaults all the pbs datastores.",
    )
    parser.add_argument(
        "--namespaces-to-ignore",
        default="",
        help="List of namespaces to ignore during checks. If not provided, default value is an empty list.",
    )
    parser.add_argument(
        "--max-depth",
        default=7,
        help="How many levels of namespaces should be operated on (0 == no recursion). The value should be between N-7. If not provided, the tool defaults value to 7 (max value).",
    )

    parser.add_argument(
        "--max-snapshot-age-hours",
        action="store",
        default="72",
        help="Specify the number of hours after which we consider that a backup is too old. If not provided, the tool defaults to 3 days.",
    )

    parser.add_argument(
        "--filling-remaining-days",
        default=30,
        help="Specify the number of days before an expiration date after which it can be critical. If not provided, the tool defaults days number to 30 days.",
    )

    parser.add_argument(
        "--timeout-seconds",
        default=30,
        help="Number of seconds until REST calls timeout.",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="If checking snapshots raises errors, exit 1, otherwise exit 0.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable 'debug' level logs.",
    )

    parser.add_argument(
        "--disable-ssl-check",
        action="store_true",
        help="Disable SSL certificate check.",
    )

    parser.add_argument("--no-errors", action="store_true", help="Print nothing if there is no errors.")

    return parser


def get_proxmox_api_handle(authinfo_file: str, disable_ssl: bool, timeout_seconds: int):
    """
    Connection with Proxmox Backup Server using proxmoxer package
    """

    with open(authinfo_file) as auth_file:
        auth_data = yaml.safe_load(auth_file)
        host = auth_data["host"]
        user = auth_data["user"]
        token_name = auth_data["token_name"]
        token_value = auth_data["token_value"]

    return ProxmoxAPI(
        host,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=not disable_ssl,
        service="pbs",
        timeout=timeout_seconds,
    )


def check_datastores(
    api_handle: ProxmoxResource,
    datastores: List[str],
    namespaces_to_ignore: str,
    max_depth: int,
    filling_remaining_days: int,
    max_snapshot_age_hours: int,
):
    """
    Depending on datastores names provided, check every snapshot to find:
    - if backups failed
    - if backups are too old
    - remaining time before to reach full storage capacity
    """

    has_errors = False

    # We create an array with all snapshots depending on datastores list
    for datastore in datastores:
        print(f"Checking datastore '{datastore}'")
        datastore_snapshots = get_all_backups(
            api_handle,
            datastore=datastore,
            namespace="",
            namespaces_to_ignore=namespaces_to_ignore.split(","),
            max_depth=max_depth,
        )

        logging.debug(
            f"Found {len(datastore_snapshots)} namespaces in datastore '{datastore}' and {sum(len(ns[1]) for ns in datastore_snapshots)} snapshots in these namespaces"
        )

        check_last_backups_expiration(datastore_snapshots, max_snapshot_age_hours)
        check_backups_status(datastore_snapshots)
        check_full_estimated_date(api_handle, datastore, int(filling_remaining_days))

        has_errors = print_detailed_errors(max_snapshot_age_hours) or has_errors

        print()

    return has_errors


def get_tool_version():
    """
    Last changelog version.

    Version value is set during build CI stage.
    """

    version = "0.3.1"

    return version


def main():
    if "--version" in sys.argv:
        print(get_tool_version())
        sys.exit(0)

    parser = get_cli_parser()
    arguments = parser.parse_args()

    logging.basicConfig()
    if arguments.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.INFO)

    api_handle = get_proxmox_api_handle(
        arguments.auth_file, arguments.disable_ssl_check, int(arguments.timeout_seconds)
    )

    if not arguments.datastores:
        datastores = [datastore["store"] for datastore in get_datastores_list(api_handle)]
    else:
        datastores = arguments.datastores.split(",")

    max_snapshot_age_hours = int(arguments.max_snapshot_age_hours)

    has_errors = check_datastores(
        api_handle,
        datastores=datastores,
        namespaces_to_ignore=arguments.namespaces_to_ignore,
        max_depth=arguments.max_depth,
        filling_remaining_days=arguments.filling_remaining_days,
        max_snapshot_age_hours=max_snapshot_age_hours,
    )

    if arguments.no_errors:
        sys.exit(0)

    if has_errors:
        print("Verification failed, exiting with error.")
        sys.exit(1)
    else:
        print("Verification successful, no errors found.")
        sys.exit(0)
