__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2025, Vanessa Sochat"
__license__ = "MIT"

import json
import os

import container_guts.utils as utils
from container_guts.main import ManifestGenerator


def generate_container_guts(uri, paths):
    """
    Generate guts. This means:

    1. We require a URI to extract.
    2. Extract paths to filesystem and make manifest
    3. Compare to database of OS bases.
    4. Subtract to find differences

    The differences are executables, etc. that were added. For now we likely
    care about MPI library paths.
    """
    # Derive an initial manifest
    cli = ManifestGenerator(tech="docker")
    if paths is None:
        return cli.run(uri, includes=["paths", "fs"])
    return cli.trace(uri, paths=paths)
