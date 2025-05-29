__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2025, Vanessa Sochat"
__license__ = "MIT"

import os

import ocifit.defaults as defaults
from ocifit import utils
from ocifit.cache import Cache

from .dockerfile import get_dockerfile, parse_dockerfile


def is_docker_uri(uri):
    """
    Check if a given string is a valid Docker image URI.
    """
    # This regex covers:
    # - Registry hostname (optional)
    # - Project name
    # - Image name
    # - Tag (optional)
    # - Digest (optional)
    docker_regex = r"^([a-zA-Z0-9.-]+/)?[a-zA-Z0-9._-]+(:[a-zA-Z0-9._-]+)?(\/[a-zA-Z0-9._-]+)*[:@][a-zA-Z0-9._-]+$"
    regex = re.compile(docker_regex)
    match = regex.match(uri)
    return bool(match)


class CompatGenerator:
    """
    Generate a Compatibility specification.
    """

    def generate(self, image, use_cache=True, model_name=defaults.model_name, save=False, uri=None):
        """
        Generate the compatibility specification.
        """
        image = os.path.abspath(image)

        # Case 1: We are give a URI Dockerfile
        if not os.path.exists(image):
            if not is_docker_uri(image):
                raise ValueError(f"{image} is not a valid Docker URI or existing filepath")
            content = get_dockerfile(image)
            uri = image
        else:
            content = utils.read_file(image)

        # Clean up the result
        result = parse_dockerfile(content, use_cache=use_cache)
        compat = {}
        for key in result:
            if not result[key]:
                continue
            compat[key] = result[key]

        # Did the user provide a uri?
        if uri is not None:
            compat["uri"] = uri

        # If we are saving and have a uri
        if save and uri is not None:
            print(f"Saving {uri} to cache...")
            cache = Cache()
            cache.save(uri, compat)
        return compat
