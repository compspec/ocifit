import ocifit.schema as schema

from .gemini import GeminiParser


class NFDParser(GeminiParser):

    @property
    def name(self):
        return "nfd"

    def get_prompt(self, content):
        return f"""
        You are a Dockerfile analyzer. Your task is to identify if a Dockerfile has software that
        indicates support for GPU, if the container needs a special networking low latency setup
        (for example, libfabric, ucx, or ofi hint yes) and identify any MPI installs, and if possible,
        the versions and library paths. Output a JSON object with the following keys:
        "base_image" for the base image, "gpu" (one of True, False, AMD or NVIDIA),
        "mpi_version" (if found) and "mpi_variant." I only want JSON as the output, without any
        additional formatting or comment. Please keep software names to single strings, without
        spaces, all in lowercase, and use dashes if you need multiple words per string. If you
        know the package manager, please provide in the format <package-manager>:<software>
        and replace the bracketed terms with strings.

        Dockerfile:
        ```
        {content}
        ```
        """

    def parse_dockerfile(
        self, content, model_name="models/gemini-2.5-flash-preview-05-20", metadata=None
    ):
        """
        Analyze a Dockerfile using a Gemma model and extract nfd dependencies
        """
        return self._parse_dockerfile(content, model_name, metadata)

    def post_parse_dockerfile(self, image, metadata):
        """
        Post processing the image and metadata will depend on the parser
        """
        unknown = ["unknown", "not-specified", "unknown"]
        # If we have it, use it to update
        for section in image:
            if image[section] in ["True", "False", True, False]:
                image[section] = bool(image[section])
        for section in metadata:
            if section not in image or section == "base_image" and image[section] in unknown:
                image[section] = metadata[section]

        # Cut out early if we won't get any metadata
        if (
            "base_image" in image
            and isinstance(image["base_image"], list)
            or image["base_image"] in unknown
        ):
            del image["base_image"]

        updated = {}
        for key, value in image.items():
            updated[f"compspec.{key}"] = value
        return schema.new_artifact([updated])
