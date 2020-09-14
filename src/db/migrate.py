import argparse
import hashlib
import importlib.util
import os
from datetime import datetime
from types import ModuleType
from typing import Set

from app.app import app
from app.database.base import EsConfig
from app.database.client import Client
from db.migration import BaseMigration

SCRIPTS_MODULES = "scripts"
VERSIONS_INDEX = "versions"


class MigratorError(Exception):
    def __init__(self, *args, **kwargs):
        super(MigratorError, self).__init__(*args, **kwargs)


class Migrator:
    es: Client

    def __init__(self, es: Client):
        self.es = es

    def run(self):
        app.logger.info("Beginning migration process")
        self.__initialize()
        not_applied_versions = self.__find_missing_versions(package_content(SCRIPTS_MODULES))
        app.logger.info(f"Missing versions: {not_applied_versions}, applying")
        self.__apply_versions(sorted(not_applied_versions))
        app.logger.info("Migration is done")

    def __initialize(self):
        if self.__check_initialized():
            app.logger.debug("Migrator is already initialized, skipping initialization")
            return

        self.es.create_index(VERSIONS_INDEX, {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "checksum": {"type": "binary"}
                }
            }
        })
        app.logger.info(f"Successfully created index {VERSIONS_INDEX}")

    def __check_initialized(self) -> bool:
        return self.es.index_exists(VERSIONS_INDEX)

    def __check_version_applied(self, version: str) -> bool:
        applied = self.es.get_document_source(VERSIONS_INDEX, version)
        if applied is None:
            return False

        if self.__get_version_checksum(version) != applied["checksum"]:
            app.logger.error(f"Wrong checksum for version {version}, did the migration changed?")
            raise MigratorError(f"wrong checksum for version {version}")

        return True

    @staticmethod
    def __get_version_checksum(version: str):
        path = module_path(SCRIPTS_MODULES, version)
        return sha1sum(path)

    def __find_missing_versions(self, version: Set[str]) -> Set[str]:
        return set([version for version in version if not self.__check_version_applied(version)])

    def __apply_versions(self, versions: [str]):
        for version in versions:
            app.logger.debug(f"Loading version {version}")
            migration = self.__load_migration(version)
            app.logger.info(f"Running migration for version {version}")
            migration.migrate(self.es)
            app.logger.info(f"Applied migration for version {version}")
            self.es.index_document(VERSIONS_INDEX, version, {
                "timestamp": int(datetime.now().timestamp()),
                "checksum": self.__get_version_checksum(version)
            })
        pass

    @staticmethod
    def __load_migration(version: str) -> BaseMigration:
        m = load_module(SCRIPTS_MODULES, version)
        return m.Migration()

    def clear(self):
        self.es.delete_index("*")
        app.logger.info("Deleted all indexes for DB")


def sha1sum(filename: str) -> str:
    h = hashlib.sha1()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def module_path(module_name: str, package_name: str) -> str:
    return load_module(module_name, package_name).__file__


def load_module(module_name: str, package_name: str) -> ModuleType:
    return importlib.import_module(f"{module_name}.{package_name}")


def package_content(package_name) -> [str]:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise ImportError('Not a package: %r', package_name)

    return set([os.path.splitext(module)[0]
                for location in spec.submodule_search_locations
                for module in os.listdir(location)
                if module.endswith(".py")])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--clear', action='store_true',
                        help='Clear whole database before running migrations')
    args = parser.parse_args()

    app.config.from_object('config')
    es = EsConfig()
    migrator = Migrator(Client(es))

    if args.clear:
        migrator.clear()

    migrator.run()
