from .gemini import GeminiParser


class SoftwareParser(GeminiParser):

    @property
    def name(self):
        return "software"

    def parse_dockerfile(
        self, content, model_name="models/gemini-2.5-flash-preview-05-20", metadata=None
    ):
        """
        Analyze a Dockerfile using a Gemma model and extract software dependencies
        """
        return self._parse_dockerfile(content, model_name, metadata)
