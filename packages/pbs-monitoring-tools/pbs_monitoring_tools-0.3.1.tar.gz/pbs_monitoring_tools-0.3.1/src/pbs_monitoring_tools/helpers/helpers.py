import time
import os
from typing import Dict, List
import datetime
from proxmoxer import ProxmoxResource
from enum import Enum, auto
import logging


class BackupError(Enum):
    VerificationFailed = auto()
    BackupTooOld = auto()
    VerificationTooOld = auto()  # Check if last verified snapshot in a group was not verified too long ago
    DatastoreEstimatedFullTooClose = auto()


_backup_errors: Dict[BackupError, List[str]] = {}


def register_error(error_key: BackupError, error: str):
    _backup_errors[error_key] = _backup_errors.get(error_key, []) + [error]


def print_detailed_errors(max_snapshot_age_hours: int):
    has_errors = False

    if BackupError.VerificationTooOld in _backup_errors:
        print(
            f"{len(_backup_errors[BackupError.VerificationTooOld])} backups are older than {max_snapshot_age_hours} hours:"
        )
        print(f"  {(os.linesep + '  ').join(sorted(_backup_errors[BackupError.VerificationTooOld]))}")
        del _backup_errors[BackupError.VerificationTooOld]
        has_errors = True

    if BackupError.VerificationFailed in _backup_errors:
        print(f"{len(_backup_errors[BackupError.VerificationFailed])} backups failed verification:")
        print(f"  {(os.linesep + '  ').join(sorted(_backup_errors[BackupError.VerificationFailed]))}")
        del _backup_errors[BackupError.VerificationFailed]
        has_errors = True

    if BackupError.DatastoreEstimatedFullTooClose in _backup_errors:
        print("\n".join(sorted(_backup_errors[BackupError.DatastoreEstimatedFullTooClose])))
        del _backup_errors[BackupError.DatastoreEstimatedFullTooClose]
        has_errors = True

    if len(_backup_errors) != 0:
        raise RuntimeError(f"Some errors were not checked: {_backup_errors}!")

    return has_errors


def get_datastores_list(api_handle: ProxmoxResource):
    """
    /admin/datastore => provide datastores list
    """

    return api_handle.admin.datastore.get()


def get_datastore_namespaces(api_handle: ProxmoxResource, datastore: str, namespace: str, max_depth: int):
    """
    Depending on the max_depth value, returns all namespaces name from provided datastore.
    """

    all_namespaces = api_handle(f"admin/datastore/{datastore}/namespace").get(
        **{"max-depth": max_depth, "parent": namespace}
    )

    return [ns for ns in all_namespaces if ns["ns"] != namespace]


def get_all_backups(
    api_handle: ProxmoxResource,
    datastore: str,
    namespace: str,
    namespaces_to_ignore: List[str],
    max_depth: int,
):
    """
    Run through all namespaces and groups to get all backups data.
    Returns tuple with namespace name and associated backups.
    """
    backups = []

    backups += [(namespace, api_handle.admin.datastore(datastore).snapshots.get(ns=namespace))]

    if max_depth > 0:
        namespaces = get_datastore_namespaces(api_handle, datastore, namespace, max_depth=1)
        for ns in namespaces:
            if ns["ns"] not in namespaces_to_ignore:
                backups += get_all_backups(
                    api_handle,
                    datastore,
                    ns["ns"],
                    namespaces_to_ignore,
                    max_depth=max_depth - 1,
                )

    return backups


def check_full_estimated_date(api_handle: ProxmoxResource, datastore: str, reminder_days: int):
    """
    Use /status/datastore-usage API endpoint to get full estimated date value.
    - datastore: datastore name from which we want to get estimated date value
    """

    datastores_usage = api_handle("status/datastore-usage").get()
    for datastore_usage in datastores_usage:
        if datastore_usage["store"] == datastore:
            estimated_full_date = datetime.datetime.fromtimestamp(datastore_usage["estimated-full-date"])

            current_date = datetime.datetime.fromtimestamp(int(time.time()))
            if estimated_full_date < current_date:
                logging.debug(f"Datastore '{datastore}' is not filling up")
                continue

            remaining_days = estimated_full_date - current_date

            if remaining_days.days < reminder_days:
                register_error(
                    BackupError.DatastoreEstimatedFullTooClose,
                    f"Storage capacity for '{datastore}' datastore will be consumed in {remaining_days.days} days.",
                )


def check_backups_status(backups: list):
    """
    Check and raise error if a backup failed.
    """
    ns: str
    groups: List[object]
    for ns, groups in backups:
        for b in groups:
            if "verification" in b:
                if b["verification"]["state"] == "failed":
                    register_error(
                        BackupError.VerificationFailed,
                        f"{ns}/{b['backup-type']}/{b['backup-id']}/{datetime.datetime.fromtimestamp(b['backup-time'], datetime.UTC).isoformat().replace('+00:00', 'Z')}",
                    )


def check_last_backups_expiration(backups: [], age_hours: int):
    """
    For provided datastore and for every namespace and backups group, get last backup time value.
    Returns dict with group value and last backup timestamp.
    """

    current_ts = datetime.datetime.now(datetime.UTC)

    groups: Dict[str, list] = {}

    for ns, backup_info in backups:
        for bi in backup_info:
            key = f"{ns}/{bi['backup-type']}/{bi['backup-id']}"
            groups[key] = groups.get(key, []) + [bi]

    for group, snapshots in groups.items():
        sorted_snapshots = sorted(snapshots, key=lambda snapshot: snapshot["backup-time"])

        most_recent_snapshot = sorted_snapshots[-1]

        backup_ts = datetime.datetime.fromtimestamp(most_recent_snapshot["backup-time"], datetime.UTC)
        datetime_difference = current_ts - backup_ts

        if datetime_difference > datetime.timedelta(hours=age_hours):
            register_error(
                BackupError.VerificationTooOld,
                f"Most recent snapshot in group '{group}' is {round(datetime_difference.total_seconds() / 86400)} days old ({backup_ts.isoformat().replace('+00:00', 'Z')}).",
            )
