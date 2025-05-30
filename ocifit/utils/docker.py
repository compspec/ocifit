import re


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
