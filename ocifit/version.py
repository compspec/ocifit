__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2025, Vanessa Sochat"
__license__ = "MIT"

__version__ = "0.0.1"
AUTHOR = "Vanessa Sochat"
NAME = "ocifit"
AUTHOR_EMAIL = "vsoch@users.noreply.github.com"
PACKAGE_URL = "https://github.com/compspec/ocifit"
KEYWORDS = "docker, containers, introspection, opencontainers, compatibility"
DESCRIPTION = "Extract and assess compatibility of container images"
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    # not using the raw model locally
    #    ("transformers", {"min_version": "4.52.0"}),
    ("protobuf", {"min_version": "5.29.3"}),
    ("google-generativeai", {"min_version": "0.8.5"}),
)


TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
