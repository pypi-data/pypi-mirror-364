import json
import os
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from joblib import Parallel, delayed

from . import helpers, steps
from .configs import Config


def database_list(project: str, instance_id: str, simulate: bool = False) -> List[str]:
    command = f'gcloud sql databases list --project="{project}" --instance="{instance_id}" --format=json'
    if simulate:
        data = '[{"name": "mysql", "name": "db-a"}]'
    else:
        p = subprocess.run(shlex.split(command), stdout=subprocess.PIPE)
        data = p.stdout.decode("utf-8")

    try:
        data = json.loads(data)
    except Exception:
        print(
            helpers.bcolors.FAIL
            + f"[project/{project}/instance/{instance_id}] Error while parsing json"
            + helpers.bcolors.ENDC
        )
        return []

    data = [x.get("name") for x in data]
    data = [
        x
        for x in data
        if x not in ["mysql", "information_schema", "performance_schema", None, "sys"]
    ]

    return data


def unpack_db_name(name: Optional[str]) -> Tuple[bool, str, str, str, str]:
    if name is None:
        print(
            helpers.bcolors.FAIL
            + "Insert a SQL Instanz connection string like <project>:<region>:<instance-id>"
            + helpers.bcolors.ENDC
        )
        return False, None, None, None, None

    values = name.split(":")
    if len(values) not in [3, 4]:
        print(
            helpers.bcolors.FAIL
            + "Insert a SQL Instanz connection string like <project>:<region>:<instance-id>"
            + helpers.bcolors.ENDC
        )
        return False, None, None, None, None

    project = values[0]
    region = values[1]
    instance_id = values[2]
    try:
        db = values[3]
    except IndexError:
        db = None
    return True, project, region, instance_id, db


def unpack_firestore_name(name: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
    if name is None:
        print(
            helpers.bcolors.FAIL
            + "Insert a Firestore connection string like <project>:<database-name>"
            + helpers.bcolors.ENDC
        )
        return False, None, None

    values = name.split(":")
    if len(values) != 2:
        print(
            helpers.bcolors.FAIL
            + "Insert a Firestore connection string like <project>:<database-name>"
            + helpers.bcolors.ENDC
        )
        return False, None, None

    project = values[0]
    database = values[1]
    return True, project, database


def instances_list(config) -> List[str]:
    databases = [x.get("databases") for x in config.load_projects()]
    databases = [x for x in databases if x is not None]
    databases = [item for sublist in databases for item in sublist]
    databases = [x for x in databases if x.strip().startswith("sql:")]
    databases = [x for x in databases if len(x.split(":")) == 5]
    databases = {":".join(x.split(":")[1:-1]) for x in databases}
    return databases


def firestore_databases_list(config) -> List[str]:
    databases = [x.get("databases") for x in config.load_projects()]
    databases = [x for x in databases if x is not None]
    databases = [item for sublist in databases for item in sublist]
    databases = [x for x in databases if x.strip().startswith("fs:")]
    databases = [x for x in databases if len(x.split(":")) == 3]
    databases = [":".join(x.split(":")[1:]) for x in databases]
    return list(set(databases))


def export_database(
    config: Config,
    project: str,
    instance_id: str,
    db: str,
    hash: Optional[str],
    simulate: bool,
) -> int:
    if hash is None:
        hash = helpers.random_string(5)
    now = datetime.now()
    bucket_name = f"{instance_id.lower()}-db-exports"
    backup_name = f"{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}/{hash}/{project}-{instance_id}-{db}.sql"
    cmd = f"gcloud sql export sql {instance_id} gs://{bucket_name}/{backup_name} --database='{db}' --project='{project}'"
    manager = steps.Manager(
        config,
        [steps.StepCommand(shlex.split(cmd))],
        simulate=simulate,
    )
    rc = manager.run()
    return rc


def export_firestore_database(
    config: Config, project: str, database: str, hash: Optional[str], simulate: bool
) -> int:
    if hash is None:
        hash = helpers.random_string(5)
    now = datetime.now()
    bucket_name = f"{project}-firestore-backup"
    backup_name = f"{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}/{hash}/{project}-{database}"
    cmd = (
        f"gcloud firestore export "
        f"gs://{shlex.quote(bucket_name)}/{shlex.quote(backup_name)} "
        f"--async --collection-ids='' --project={shlex.quote(project)}"
    )
    if database != "(default)":
        cmd += f" --database={shlex.quote(database)}"
    manager = steps.Manager(
        config,
        [steps.StepCommand(shlex.split(cmd))],
        simulate=simulate,
    )
    rc = manager.run()
    return rc


def cli_main(args, config) -> int:
    if args.action == "sql-init":
        is_success, project, region, instance_id, _ = unpack_db_name(args.name)
        if not is_success:
            return 1

        bucket_name = f"{instance_id.lower()}-db-exports"

        print(f"- Bucket gs://{bucket_name} wird angelegt")
        manager = steps.Manager(
            config,
            [
                steps.StepCommand(
                    shlex.split(
                        f"gcloud storage buckets create gs://{bucket_name} --project='{project}' --location='{region}'"
                    ),
                    can_fail=True,
                    retry=0,
                ),
            ],
            simulate=args.simulate,
        )
        rc = manager.run()
        if rc != 0:
            return rc

        print(
            "- dem Dienstkonto des SQL Servers Administrator Rechte für Storage im Bucket geben"
        )
        print(
            "- im Bucket den Lebenszyklus einstellen, das die Dateien nach 14 Tagen gelöscht werden"
        )
        print(
            f"https://console.cloud.google.com/storage/browser/{bucket_name};tab=lifecycle?project={project}"
        )

    elif args.action == "sql-list-instances":
        instances = instances_list(config)

        for instance in instances:
            print(f"- {instance}")

    elif args.action == "sql-list-databases":
        is_success, project, region, instance_id, _ = unpack_db_name(args.name)
        if not is_success:
            return 1

        databases = database_list(project, instance_id, args.simulate)
        print(databases)
    elif args.action == "sql-dump":
        h = helpers.Health()
        h.start()

        is_success = True
        datas = []
        if args.name is None:
            instances = instances_list(config)
            datas = [
                x.get("databases")
                for x in config.load_projects()
                if x.get("databases") is not None
            ]
            datas = [item for sublist in datas for item in sublist]
            datas = [x[4:] for x in datas if x.strip().startswith("sql:")]
            datas = [unpack_db_name(x) for x in datas]
            datas = {
                f"project/{project}/locations/{region}/instances/{instance_id}": {
                    "project": project,
                    "region": region,
                    "instance_id": instance_id,
                    "databases": [],
                }
                for _, project, region, instance_id, _ in datas
            }
            datas = [datas[x] for x in datas.keys()]
            datas = [
                {
                    **x,
                    "databases": database_list(
                        x["project"], x["instance_id"], args.simulate
                    ),
                }
                for x in datas
            ]
            if len([x for x in datas if len(x["databases"]) <= 0]):
                is_success = False  # kompletter abbruch eine instance konnten die dbs nicht geladen werden
        else:
            is_success, project, region, instance_id, db = unpack_db_name(args.name)
            if not is_success:
                return 1
            if db is None:
                databases = database_list(project, instance_id, args.simulate)
            else:
                databases = [db]
            datas = [
                {
                    "project": project,
                    "region": region,
                    "instance_id": instance_id,
                    "databases": databases,
                }
            ]

        def run_export(config, instance: dict, hash: str, is_simulate=False):
            databases = [
                {
                    "name": x,
                    "status": export_database(
                        config,
                        instance.get("project"),
                        instance.get("instance_id"),
                        x,
                        hash,
                        is_simulate,
                    ),
                }
                for x in instance.get("databases", [])
            ]
            return {
                **instance,
                **{
                    "databases": databases,
                },
            }

        hash = helpers.random_string(5)
        datas = Parallel(backend="threading", n_jobs=-1)(
            delayed(run_export)(config, x, hash, args.simulate) for x in datas
        )

        print("Results:")
        for instance in datas:
            if len(instance.get("databases", [])) <= 0:
                is_success = False
                print(
                    helpers.bcolors.FAIL
                    + f"- {instance.get('project')}/{instance.get('instance_id')} - no databases found"
                    + helpers.bcolors.ENDC
                )
                continue

            print(f"- {instance.get('project')}/{instance.get('instance_id')}")
            for db in instance.get("databases", []):
                if db.get("status") != 0:
                    is_success = False
                    print(
                        helpers.bcolors.FAIL
                        + f"  - {db.get('name')}"
                        + helpers.bcolors.ENDC
                    )
                else:
                    print(
                        helpers.bcolors.OKGREEN
                        + f"  - {db.get('name')}"
                        + helpers.bcolors.ENDC
                    )

        if not is_success:  # check global is ok
            return 1

        h.finish()
        return 0
    elif args.action == "sql-download":
        instances = instances_list(config)
        home_dir = os.path.expanduser("~")

        def download_instances_backups(config: Config, instance: str) -> int:
            is_success, _, _, instance_id, _ = unpack_db_name(instance)
            if not is_success:
                return 1
            bucket_name = f"{instance_id.lower()}-db-exports"
            backup_path = f"{home_dir}/db_dumps/{bucket_name}"
            manager = steps.Manager(
                config,
                [
                    steps.StepCommand(
                        shlex.split(f"mkdir -p {backup_path}"),
                        can_fail=True,
                        retry=0,
                    ),
                    steps.StepCommand(
                        shlex.split(
                            f"gsutil rsync -r -u gs://{bucket_name}/ {backup_path}"
                        ),
                        can_fail=True,
                        retry=0,
                    ),
                ],
                simulate=args.simulate,
            )
            rc = manager.run()
            return rc

        res = Parallel(backend="threading", n_jobs=-1)(
            delayed(download_instances_backups)(config, instance)
            for instance in instances
        )
        if any(x != 0 for x in res):
            print("Ein Export ist fehlerhaft gelaufen.")
    elif args.action == "sql-push-to-drive":
        instances = instances_list(config)
        home_dir = os.path.expanduser("~")

        destination = args.name
        destination_path = Path(destination)
        if not destination_path.exists():
            print(
                helpers.bcolors.FAIL
                + f"Path not exists: {destination}"
                + helpers.bcolors.ENDC
            )

        manager = steps.Manager(
            config,
            [
                steps.StepCommand(
                    shlex.split(
                        f"rsync -av --ignore-existing {home_dir}/db_dumps/ {destination}"
                    ),
                    can_fail=True,
                    retry=0,
                ),
            ],
            simulate=args.simulate,
        )
        rc = manager.run()
        if rc != 0:
            return rc
    elif args.action == "fs-init":
        is_success, project, database = unpack_firestore_name(args.name)
        if not is_success:
            return 1

        bucket_name = f"{project}-firestore-backup"

        print(f"- Bucket gs://{bucket_name} wird angelegt")
        manager = steps.Manager(
            config,
            [
                steps.StepCommand(
                    shlex.split(
                        f"gcloud storage buckets create gs://{bucket_name} --project='{project}' --location='europe-west3'"
                    ),
                    can_fail=True,
                    retry=0,
                ),
            ],
            simulate=args.simulate,
        )
        rc = manager.run()
        if rc != 0:
            return rc

        print(
            "- dem Dienstkonto des Firestore Services Storage Admin Rechte für den Bucket geben"
        )
        print(
            "- im Bucket den Lebenszyklus einstellen, das die Dateien nach 14 Tagen gelöscht werden"
        )
        print(
            f"https://console.cloud.google.com/storage/browser/{bucket_name};tab=lifecycle?project={project}"
        )
    elif args.action == "fs-list-databases":
        databases = firestore_databases_list(config)

        for database in databases:
            print(f"- {database}")
    elif args.action == "fs-dump":
        h = helpers.Health()
        h.start()

        is_success = True
        datas = []
        if args.name is None:
            # Get all Firestore databases from config
            databases = firestore_databases_list(config)
            datas = [
                {
                    "project": db.split(":")[0],
                    "database": db.split(":")[1],
                }
                for db in databases
            ]
        else:
            is_success, project, database = unpack_firestore_name(args.name)
            if not is_success:
                return 1
            datas = [
                {
                    "project": project,
                    "database": database,
                }
            ]

        def run_firestore_export(config, instance: dict, hash: str, is_simulate=False):
            return {
                **instance,
                "status": export_firestore_database(
                    config,
                    instance.get("project"),
                    instance.get("database"),
                    hash,
                    is_simulate,
                ),
            }

        hash = helpers.random_string(5)
        datas = Parallel(backend="threading", n_jobs=-1)(
            delayed(run_firestore_export)(config, x, hash, args.simulate) for x in datas
        )

        print("Results:")
        for instance in datas:
            if instance.get("status") != 0:
                is_success = False
                print(
                    helpers.bcolors.FAIL
                    + f"- {instance.get('project')}/{instance.get('database')}"
                    + helpers.bcolors.ENDC
                )
            else:
                print(
                    helpers.bcolors.OKGREEN
                    + f"- {instance.get('project')}/{instance.get('database')}"
                    + helpers.bcolors.ENDC
                )

        if not is_success:
            return 1

        h.finish()
        return 0
    elif args.action == "fs-download":
        databases = firestore_databases_list(config)
        home_dir = os.path.expanduser("~")

        def download_firestore_backups(config: Config, database: str) -> int:
            project = database.split(":")[0]
            bucket_name = f"{project}-firestore-backup"
            backup_path = f"{home_dir}/db_dumps/{bucket_name}"
            manager = steps.Manager(
                config,
                [
                    steps.StepCommand(
                        shlex.split(f"mkdir -p {backup_path}"),
                        can_fail=True,
                        retry=0,
                    ),
                    steps.StepCommand(
                        shlex.split(
                            f"gsutil rsync -r -u gs://{bucket_name}/ {backup_path}"
                        ),
                        can_fail=True,
                        retry=0,
                    ),
                ],
                simulate=args.simulate,
            )
            rc = manager.run()
            return rc

        res = Parallel(backend="threading", n_jobs=-1)(
            delayed(download_firestore_backups)(config, database)
            for database in databases
        )
        if any(x != 0 for x in res):
            print("Ein Export ist fehlerhaft gelaufen.")

    return 0
