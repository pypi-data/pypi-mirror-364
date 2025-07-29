import mlflow
from mlflow.models.signature import infer_signature

from mlflow_migration.common.model_utils import is_unity_catalog_model
from mlflow_migration.common.mlflow_utils import MlflowTrackingUriTweak
from tests.utils_test import mk_test_object_name_default
from tests import sklearn_utils
from tests.core import TestContext
from tests import utils_test
from .init_tests import workspace_src


def mk_experiment_name(workspace=workspace_src):
    return f"{workspace.base_dir}/{mk_test_object_name_default()}"


def mk_uc_model_name(workspace=workspace_src):
    return f"{workspace.uc_full_schema_name}.{mk_test_object_name_default()}"


def mk_model_name(workspace, is_uc=False):
    if is_uc:
        return mk_uc_model_name(workspace)
    else:
        return mk_test_object_name_default()


def create_experiment(client):
    exp_id = client.create_experiment(mk_experiment_name(), tags={"ocean": "southern"})
    return client.get_experiment(exp_id)


def create_run(client, experiment_id):
    max_depth = 4
    model = sklearn_utils.create_sklearn_model(max_depth)
    predictions = model.predict(sklearn_utils.X_test)
    signature = infer_signature(sklearn_utils.X_train, predictions)

    with MlflowTrackingUriTweak(client):
        with mlflow.start_run(experiment_id=experiment_id) as run:
            mlflow.log_param("max_depth", max_depth)
            mlflow.log_metric("rmse", 0.789)
            mlflow.set_tag("my_tag", "my_val")
            mlflow.sklearn.log_model(model, "model", signature=signature)
            mlflow.set_tag("south_america", "aconcagua")
            with open("info.txt", "w", encoding="utf-8") as f:
                f.write("Hi artifact")
            mlflow.log_artifact("info.txt")
    return client.get_run(run.info.run_id)


def create_version(client, model_name, stage=None, archive_existing_versions=False):
    exp_src = create_experiment(client)
    run = create_run(client, exp_src.experiment_id)
    source = f"{run.info.artifact_uri}/model"
    desc = "My model desc"
    tags = {"city": "copan"}
    model = _create_registered_model(client, model_name, tags, desc)
    tags = {"city": "yaxchilan", "uuid": utils_test.mk_uuid()}

    with MlflowTrackingUriTweak(
        client
    ):  # needed since client.registry_uri is ignored :(
        vr = client.create_model_version(
            model_name, source, run.info.run_id, description="my version", tags=tags
        )

    if is_unity_catalog_model(
        model_name
    ):  # Aliases are disabled for Non-UC Databricks MLflow
        alias = f"alias_{utils_test.mk_uuid()}"
        client.set_registered_model_alias(model_name, alias, vr.version)
    else:
        if stage:
            vr = client.transition_model_version_stage(
                model_name, vr.version, stage, archive_existing_versions
            )
    vr = client.get_model_version(
        model_name, vr.version
    )  # NOTE: since transition_model_version_stage returns no tags!
    return vr, model


def _create_registered_model(client, model_name, tags, desc):
    from mlflow.exceptions import RestException

    try:
        return client.create_registered_model(model_name, tags, desc)
    except RestException:
        return client.get_registered_model(model_name)


def mk_one_workspace_test_context(test_context):
    return TestContext(
        test_context.mlflow_client_src,
        test_context.mlflow_client_src,
        test_context.dbx_client_src,
        test_context.dbx_client_src,
        test_context.output_dir,
        test_context.output_run_dir,
    )
