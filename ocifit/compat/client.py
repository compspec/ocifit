__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2025, Vanessa Sochat"
__license__ = "MIT"

import os

import ocifit.defaults as defaults
from ocifit import utils
from ocifit.cache import Cache
from ocifit.parsers import get_parser

from .dockerfile import get_dockerfile


class CompatGenerator:
    """
    Generate a Compatibility specification.
    """

    def __init__(self, parser, use_cache=True):
        """
        Setup a compatibility generator.
        """
        self.use_cache = use_cache

        # parser here is just the name to organize the cache
        self.cache = Cache(parser)

        # The parser can use the cache too.
        self.parser = get_parser(parser)(self.cache)

    def generate(self, image, model_name=defaults.model_name, save=False, uri=None):
        """
        Generate the compatibility specification.
        """
        image = os.path.abspath(image)

        # Case 1: We are give a URI Dockerfile
        if not os.path.exists(image):
            if not utils.is_docker_uri(image):
                raise ValueError(f"{image} is not a valid Docker URI or existing filepath")
            content = get_dockerfile(image)
            uri = image
        else:
            content = utils.read_file(image)

        # Clean up the result
        result = self.parser.parse_dockerfile(content)
        compat = {}
        for key in result:
            if not result[key]:
                continue
            compat[key] = result[key]
            if isinstance(compat[key], list):
                compat[key].sort()

        # Did the user provide a uri?
        if uri is not None:
            compat["uri"] = uri

        # If we are saving and have a uri
        if save and uri is not None:
            print(f"Saving {uri} to cache...")
            cache = Cache()
            cache.save(uri, compat)
        return compat
