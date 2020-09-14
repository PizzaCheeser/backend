import json

from app.app import app
from app.database.client import Client
from db.migration import BaseMigration

BACKUP_BUCKET = {
    "dev": "es-dev-backup",
    "prod": "es-prod-backup",
}

REPOSITORY_NAME = {
    "dev": "dev-backup",
    "prod": "prod-backup",
}

ENVS = ["dev", "prod"]


class Migration(BaseMigration):
    def migrate(self, es: Client):
        current_environment = app.config["ENVIRONMENT"]

        if current_environment == "local":
            app.logger.error("Local environment, skipping backup configuration")
            return

        for env in ENVS:
            r = es.client.put(
                f"{es.es.url}_snapshot/{REPOSITORY_NAME[env]}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "type": "s3",
                        "settings": {
                            "bucket": BACKUP_BUCKET[env],
                            "endpoint": app.config["MINIO_ENDPOINT"],
                            "protocol": "http",
                            "path_style_access": True,
                            "readonly": env != current_environment,
                        }
                    }
                ))
            r.raise_for_status()
            app.logger.info(f"Created repository {REPOSITORY_NAME[current_environment]}")

        r = es.client.put(
            f"{es.es.url}_slm/policy/weekly-snapshots",
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "schedule": "0 30 1 ? * MON",
                    "name": "<weekly-snap-{now/d}>",
                    "repository": REPOSITORY_NAME[current_environment],
                    "config": {
                        "indices": ["*"],
                    },
                    "retention": {
                        "expire_after": "30d",
                        "min_count": 5,
                        "max_count": 50,
                    },
                }
            )
        )
        r.raise_for_status()
        app.logger.info(f"Created weekly backup schedule")

    def roll_back(self, es: Client):
        r = es.client.delete(f"{es.es.url}_slm/policy/weekly-snapshots")
        r.raise_for_status()
        for env in ENVS:
            r = es.client.delete(f"{es.es.url}_snapshot/{REPOSITORY_NAME[env]}")
            r.raise_for_status()

