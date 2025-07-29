import os
import pytest
import mlflow

from mlflow_migration.common.iterators import SearchRegisteredModelsIterator
from mlflow_migration.common import MlflowExportImportException
from mlflow_migration.common import utils, model_utils
from mlflow_migration.client.http_client import DatabricksHttpClient
from tests import utils_test
from tests.core import TestContext
from tests.databricks.unity_catalog_client import UnityCatalogClient
from tests.databricks.includes import Dict2Class

_logger = utils.getLogger(__name__)


# Skip Databricks cleanup calls to avoid 429
_skip_cleanup = os.environ.get("MLFLOW_MIGRATION_SKIP_CLEANUP")
_logger.info(f"_skip_cleanup: {_skip_cleanup}")


_cfg = utils_test.read_config_file()
cfg = Dict2Class(_cfg)


class Workspace:
    def __init__(self, cfg_ws):
        self.cfg = cfg_ws
        self.base_dir = self.cfg.base_dir
        tracking_profile = self.cfg.profile.replace(
            "databricks-uc", "databricks"
        )  # no "-uc" for tracking
        self.mlflow_client = mlflow.MlflowClient(tracking_profile, self.cfg.profile)
        self.dbx_client = DatabricksHttpClient(self.mlflow_client.tracking_uri)
        self.uc_dbx_client = UnityCatalogClient(self.dbx_client)

        _logger.info("Workspace:")
        _logger.info(f"  base_dir: {self.base_dir}")
        _logger.info(f"  mlflow_client: {self.mlflow_client}")
        _logger.info(f"  dbx_client: {self.dbx_client}")

        self.is_uc = self.cfg.profile.startswith("databricks-uc")
        _logger.info(f"  is_uc: {self.is_uc}")
        if hasattr(self.cfg, "uc_schema"):
            self.uc_catalog_name, self.uc_schema_name = self.cfg.uc_schema.split(".")
            self.uc_full_schema_name = self.cfg.uc_schema
            _logger.info(f"  uc_full_schema_name: {self.uc_full_schema_name}")

    def __repr__(self):
        return str({k: v for k, v in self.__dict__.items()})


workspace_src = Workspace(cfg.workspace_src)
workspace_dst = Workspace(cfg.workspace_dst)

utils.calling_databricks(workspace_src.dbx_client)


def init_tests():
    _init_workspace(workspace_src)
    _init_workspace(workspace_dst)


def _init_workspace(ws):
    _create_base_directory(ws)
    if ws.is_uc:
        try:
            ws.uc_dbx_client.create_schema(ws.uc_catalog_name, ws.uc_schema_name)
        except MlflowExportImportException:
            _logger.warning(f"{ws.uc_dbx_client}: schema exists: '{ws.cfg.uc_schema}'")


def _create_base_directory(ws):
    """Create test base workspace directory for experiments"""
    params = {"path": ws.base_dir}
    _logger.info(f"{ws.dbx_client}: Creating {ws.base_dir}")
    ws.dbx_client.post("workspace/mkdirs", params)


def _cleanup():
    """Delete all test models and experiments"""
    if not _skip_cleanup:
        _logger.info("Databricks cleanup")
        _cleanup_ws(workspace_src)
        _cleanup_ws(workspace_dst)
    else:
        _logger.warning("Skipping Databricks cleanup")


def _cleanup_ws(ws):
    _delete_directory(ws)
    if ws.is_uc:
        _delete_models_uc(ws)
    else:
        _delete_models_non_uc(ws)


def _delete_models_non_uc(ws):
    filter = "name like 'test_exim_%'"
    models = SearchRegisteredModelsIterator(ws.mlflow_client, filter=filter)
    models = list(models)
    _logger.info(f"{ws.dbx_client}: Deleting {len(models)} non-UC models")
    for model in models:
        _logger.info(f"{ws.dbx_client}: Deleting model '{model.name}'")
        model_utils.delete_model(ws.mlflow_client, model.name)


def _delete_models_uc(ws):
    model_names = ws.uc_dbx_client.list_model_names(
        ws.uc_catalog_name, ws.uc_schema_name
    )
    _logger.info(f"{ws.dbx_client}: Deleting {len(model_names)} UC model")
    for name in model_names:
        _logger.info(f"{ws.dbx_client}: Deleting model '{name}'")
        model_utils.delete_model(ws.mlflow_client, name)


def _delete_directory(ws):
    """Deletes notebooks in test based directory"""
    params = {"path": ws.base_dir, "recursive": True}
    _logger.info(f"{ws.dbx_client}: Deleting {ws.base_dir}")
    try:
        ws.dbx_client.post("workspace/delete", params)
    except MlflowExportImportException as e:
        _logger.warning(f"{ws.dbx_client}: Delete workspace API call: {e}")


@pytest.fixture(scope="session")
def test_context():
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        assert mlflow.get_tracking_uri() is not None
        output_dir = os.environ.get(
            "MLFLOW_MIGRATION_OUTPUT_DIR", None
        )  # for debugging
        if output_dir:
            utils_test.create_output_dir(output_dir)
        else:
            output_dir = tmpdir
        _logger.info(f"output_dir: {output_dir}")
        yield TestContext(
            workspace_src.mlflow_client,
            workspace_dst.mlflow_client,
            workspace_src.dbx_client,
            workspace_dst.dbx_client,
            output_dir,
            os.path.join(output_dir, "run"),
        )
    _cleanup()


# Initialize the testing world
init_tests()
