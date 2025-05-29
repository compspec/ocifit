import json
import os
import re

import ocifit.utils as utils


class Cache:
    """
    Manage image compatibility metadata.
    The cache directory is ~/.ocifit.
    """

    def __init__(self):
        """
        Initializes the Cache object.
        Creates the cache directory if it doesn't exist.
        """
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".ocifit")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def load(self):
        """
        Load all images from the cache
        """
        items = {}
        for uri in os.listdir(self.cache_dir):
            path = os.path.join(self.cache_dir, uri)
            metadata = utils.read_json(path)
            items[metadata["uri"]] = metadata
        return items

    def uri_to_path(self, uri):
        """
        Convert a URI to a path.
        """
        uri = re.split("(@| )", uri)[0]
        filename = re.sub("(/|:)", "-", uri)
        return os.path.join(self.cache_dir, filename + ".json")

    def get(self, uri):
        """
        Look for a compatibility artifact in the cache.

        We start with a URI and transform to a path.
        """
        filepath = self.uri_to_path(uri)
        if os.path.exists(filepath):
            try:
                return utils.read_json(filepath)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {filepath}. File may be corrupted.")
                return None
        else:
            return None

    def save(self, uri, data):
        """
        Writes a compatibility spec to the cache.
        """
        filepath = self.uri_to_path(uri)
        try:
            utils.write_json(data, filepath)
        except Exception as e:
            print(f"Error writing to {filepath}: {e}")
