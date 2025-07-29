from mlflow_migration.common import MlflowExportImportException
from mlflow_migration.common import utils
from mlflow_migration.common.filesystem import mk_local_path

_logger = utils.getLogger(__name__)


def read_rename_file(path):
    with open(mk_local_path(path), "r", encoding="utf-8") as f:
        dct = {}
        for line in f:
            toks = line.rstrip().split(",")
            dct[toks[0]] = toks[1]
        return dct


def rename(name, replacements, object_name="object"):
    if not replacements:
        return name
    for k, v in replacements.items():
        if k != "" and name.startswith(k):
            new_name = name.replace(k, v)
            _logger.info(f"Renaming {object_name} '{name}' to '{new_name}'")
            return new_name
    return name


def get_renames(filename_or_dict):
    if filename_or_dict is None:
        return None
    if isinstance(filename_or_dict, str):
        return read_rename_file(filename_or_dict)
    elif isinstance(filename_or_dict, dict):
        return filename_or_dict
    else:
        raise MlflowExportImportException(
            f"Unknown name replacement type '{type(filename_or_dict)}'",
            http_status_code=400,
        )
