from datetime import datetime


def new_artifact(compats):
    return {
        "schemaVersion": "0.1.0",
        "mediaType": "application/vnd.oci.image.compatibilities.v1+json",
        "compatibilities": compats,
        "annotations": {
            "oci.opencontainers.image.created": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }
