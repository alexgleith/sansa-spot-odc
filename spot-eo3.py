#!/usr/bin/env python3

import json
import logging
from datetime import datetime
from pathlib import Path

import click
import rasterio
from odc.index import odc_uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
)


def process_file(in_file: Path):
    """Create an EO3 metadata document for the input file
    e.g. S6-E29S27-20140316-075045-P-SEN-SPOT6_20200221_102757z1uilvbwxvx8_1_ORTHO_PSH.pix
    """

    file_name = in_file.stem
    id = odc_uuid("sansa-spot", "1.0.0", [file_name])

    epsg_code = None
    grid = None

    with rasterio.open(str(in_file)) as src:
        epsg_code = src.crs.to_epsg()
        grid = {
            "shape": src.shape,
            "transform": list(src.transform),
        }

    # We should add a lot more information here
    properties = {
        "platform": file_name.split("-")[0],
        "region_code": file_name.split("-")[1],
        "datetime": datetime.strftime(
            datetime.strptime(
                file_name.split("-")[2] + file_name.split("-")[3], "%Y%m%d%H%M%S"
            ),
            "%Y-%m-%dT%H%M%S",
        ),
    }

    bands = {
        "red": {"path": str(in_file.relative_to(in_file.parents[0])), "band": 1},
        "green": {"path": str(in_file.relative_to(in_file.parents[0])), "band": 2},
        "blue": {"path": str(in_file.relative_to(in_file.parents[0])), "band": 3},
        "nir": {"path": str(in_file.relative_to(in_file.parents[0])), "band": 4},
    }

    eo3_doc = {
        "$schema": "https://schemas.opendatacube.org/dataset",
        "id": str(id),
        "label": in_file.stem,
        "crs": f"epsg:{epsg_code}",
        "grids": {"default": grid},
        "product": {"name": "spot"},
        "properties": properties,
        "measurements": bands,
        "lineage": {},
        "accessories": {},
    }

    # Write eo3_doc to JSON
    logging.info(f"Finished processing file {in_file}, writing JSON")
    out_file = in_file.with_suffix(".odc-dataset.json")
    out_file.write_text(json.dumps(eo3_doc, indent=2))


@click.command("spot-eo3")
@click.argument("input_directory", type=str, nargs=1)
def cli(input_directory):
    logging.info(f"Starting up, searching in {input_directory}")

    files_to_process = Path(input_directory).glob("*.pix")

    for in_file in files_to_process:
        logging.info(f"Processing {in_file}")
        process_file(in_file)


if __name__ == "__main__":
    cli()
