# SANSA SPOT indexing

This repo contains a script that sets up EO3 JSON documents for SPOT images.

To use it, do the following.

1. Add the product `datacube product add spot.odc-product.yaml`
2. Create metadata docs `python3 spot-eo3.py data`
3. Index the docs `datacube dataset add data/*.json`
4. Run the notebook, or a Python script, to load data.

Todo:

* Ensure that all metadata is captured in the `parameters` in the `spot-eo3.py` file
