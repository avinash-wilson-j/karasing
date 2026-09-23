"""A Google Cloud Python Pulumi program"""

"""Infrastructure BigQuery pour KaraSing (sandbox, sans facturation)."""

import pulumi
from pulumi_gcp import bigquery

LOCATION = "europe-west1"
LAYERS = ["raw", "staging", "dim", "facts", "marts"]

datasets = {}
for layer in LAYERS:
    datasets[layer] = bigquery.Dataset(
        f"karasing_{layer}",
        dataset_id=layer,
        location=LOCATION,
        description=f"Couche {layer} du projet KaraSing (sandbox, test SQLMesh)",
    )

for layer, ds in datasets.items():
    pulumi.export(f"dataset_{layer}", ds.dataset_id)
