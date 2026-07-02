""" top level run script """
import json
import logging
import os
from pathlib import Path

from dynamic_foraging_processing.pipeline import Pipeline
from dynamic_foraging_processing.raw_data_loader import RawDataLoader
from log_schema import setup_logging
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class InputSettings(BaseSettings, cli_parse_args=True):
    """
    Settings for VR Foraging Primary Data NWB Packaging
    """

    input_directory: Path = Field(
        default=Path("/data/"), description="Directory where data is"
    )
    output_directory: Path = Field(
        default=Path("/results/"), description="Output directory"
    )

def run() -> None:
    """
    Entrypoint for executing
    """
    settings = InputSettings()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    raw_data_path = tuple(settings.input_directory.glob("*"))
    if not raw_data_path:
        raise FileNotFoundError(
            "No data asset attached"
        )
    
    if len(raw_data_path) > 1:
        raise ValueError(
            "Multiple data assets attached"
        )
    raw_data_path = raw_data_path[0]
    data_description_path = raw_data_path / "data_description.json"
    if not data_description_path.exists():
        raise FileNotFoundError(
            "No data description file found in data folder"
        )
    with open(data_description_path, "r") as f:
        data_description = json.load(f)

    acquisition_name = data_description["name"]
    process_name = os.getenv("PROCESS_NAME", "dynamic-foraging-qc")
    pipeline_name = os.getenv("PIPELINE_NAME", "")
    setup_logging(
        (Path(__file__).parent / "cloud_watch_config.yml").as_posix(),
        model={
            "acquisition_name": acquisition_name,
            "process_name": process_name,
            "pipeline_name": pipeline_name    
        },
    )

    logger.info("Begin QC ...", extra={"event_type": "stage_start"})

    logger.info(
        f"Found session {data_description["name"]}. "
        "Running QC"
    )
    raw_data_loader = RawDataLoader(raw_data_path)
    pipeline_runner = Pipeline(raw_data_loader)
    pipeline_runner.run_qc(
        settings.output_directory,
        folder_directory="dynamic-foraging-qc"
    )
    logger.info(
        "Finished QC. Written to results"
    )
    logger.info("Pipeline stage completed", extra={"event_type": "stage_complete"})

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception("Pipeline stage failed", extra={"event_type": "stage_error"})