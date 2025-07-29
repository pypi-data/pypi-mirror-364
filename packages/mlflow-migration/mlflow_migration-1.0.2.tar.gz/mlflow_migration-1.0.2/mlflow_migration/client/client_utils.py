import mlflow
from .http_client import HttpClient, MlflowHttpClient, DatabricksHttpClient


def create_http_client(mlflow_client, model_name=None):
    """
    Create MLflow HTTP client from MlflowClient.
    If model_name is a Unity Catalog (UC) model, the returned client is UC-enabled.
    """
    from mlflow_migration.common import model_utils

    creds = mlflow_client._tracking_client.store.get_host_creds()
    if model_name and model_utils.is_unity_catalog_model(model_name):
        return HttpClient("api/2.0/mlflow/unity-catalog", creds.host, creds.token)
    else:
        return MlflowHttpClient(creds.host, creds.token)


def create_dbx_client(mlflow_client):
    """
    Create Databricks HTTP client from MlflowClient.
    """
    creds = mlflow_client._tracking_client.store.get_host_creds()
    return DatabricksHttpClient(creds.host, creds.token)


def create_mlflow_client():
    """
    Create MLflowClient. If MLFLOW_TRACKING_URI is UC, then set MlflowClient.tracking_uri to the non-UC variant.
    """
    registry_uri = mlflow.get_registry_uri()
    if registry_uri:
        tracking_uri = mlflow.get_tracking_uri()
        nonuc_tracking_uri = tracking_uri.replace(
            "databricks-uc", "databricks"
        )  # NOTE: legacy
        return mlflow.MlflowClient(nonuc_tracking_uri, registry_uri)
    else:
        return mlflow.MlflowClient()
