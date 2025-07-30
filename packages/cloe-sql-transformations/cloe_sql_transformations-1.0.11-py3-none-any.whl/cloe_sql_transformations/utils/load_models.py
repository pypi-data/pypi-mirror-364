import json
import pathlib
from typing import Any

from cloe_metadata import base
from cloe_metadata.shared.modeler import custom_dataflow, dataflow
from cloe_metadata.utils import model_transformer


def _preprocess_dataflow_json(json_data: dict[str, Any]) -> dict[str, Any]:
    """
    Preprocess dataflow JSON to fix field name casing issues.

    Converts GUI camelCase fields to match Pydantic model aliases:
    - "postProcessingSQL" -> "postProcessingSql"
    - "preProcessingSQL" -> "preProcessingSql"
    """
    if "postProcessingSQL" in json_data:
        json_data["postProcessingSql"] = json_data.pop("postProcessingSQL")

    if "preProcessingSQL" in json_data:
        json_data["preProcessingSql"] = json_data.pop("preProcessingSQL")

    return json_data


def _preprocess_json_files(input_model_path: pathlib.Path) -> None:
    """
    Preprocess all dataflow JSON files to fix field name casing.
    """
    dataflow_dir = input_model_path / "modeler" / "dataflows"

    if not dataflow_dir.exists():
        return

    for json_file in dataflow_dir.glob("*.json"):
        try:
            with json_file.open(encoding="utf-8") as f:
                data = json.load(f)

            # Only preprocess if it contains the problematic fields
            if "postProcessingSQL" in data or "preProcessingSQL" in data:
                data = _preprocess_dataflow_json(data)

                with json_file.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

        except (json.JSONDecodeError, OSError) as e:
            # Log error but continue processing other files
            print(f"Warning: Could not preprocess {json_file}: {e}")


def load_models(
    input_model_path: pathlib.Path,
) -> tuple[
    list[dataflow.Dataflow],
    list[custom_dataflow.CustomDataflow],
    base.SQLTemplates,
    base.ConversionTemplates,
]:
    # Preprocess JSON files to fix field name casing issues between GUI and Pydantic model
    _preprocess_json_files(input_model_path)

    flows, p_errors = base.Flows.read_instances_from_disk(input_model_path)
    databases, d_errors = base.Databases.read_instances_from_disk(input_model_path)
    tenants, t_errors = base.Tenants.read_instances_from_disk(input_model_path)
    conversion_templates, c_errors = base.ConversionTemplates.read_instances_from_disk(input_model_path)
    sql_templates, sql_errors = base.SQLTemplates.read_instances_from_disk(input_model_path)
    trans_dataflows, t_pp_errors = model_transformer.transform_power_pipes_to_shared(
        base_obj_collection=flows,
        databases=databases,
        tenants=tenants,
        conversion_templates=conversion_templates,
        sql_templates=sql_templates,
    )
    (
        trans_custom_dataflows,
        t_sp_errors,
    ) = model_transformer.transform_simple_pipes_to_shared(
        base_obj_collection=flows,
        databases=databases,
    )
    if (
        len(p_errors) > 0
        or len(d_errors) > 0
        or len(c_errors) > 0
        or len(t_errors) > 0
        or len(sql_errors) > 0
        or len(t_pp_errors) > 0
        or len(t_sp_errors) > 0
    ):
        raise ValueError(
            "The provided models did not pass validation, please run validation.",
        )

    return (
        trans_dataflows,
        trans_custom_dataflows,
        sql_templates,
        conversion_templates,
    )
