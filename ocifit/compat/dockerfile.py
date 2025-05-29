import json
import os

import requests

import ocifit.defaults as defaults
from ocifit.cache import Cache

try:
    import google.generativeai as genai
except ImportError:
    raise ValueError("Please install google-generativeai")

generation_config = {
    # Lower temperature for more deterministic, less creative output
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    # # Increased to handle potentially long script outputs
    "max_output_tokens": 10000,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

token = os.environ.get("GEMINI_TOKEN")
if not token:
    raise ValueError("This module requires a GEMINI_TOKEN exported in the environment.")

genai.configure(api_key=token)

# model_names = [x.name for x in list(genai.list_models())]
# print(model_names)

# Base image cache
base_image_cache = {}
empty_images = {}
cache = None


def parse_dockerfile(
    content, use_cache=False, model_name="models/gemini-2.5-flash-preview-05-20", metadata=None
):
    """
    Analyzes a Dockerfile using a Gemma model from Hugging Face and extracts software dependencies,
    formatting the output as JSON.

    Args:
        dockerfile_path (str): The path to the Dockerfile.
        model_name (str): The name of the Gemma model on Hugging Face.

    Returns:
        str: A JSON string representing the software dependencies.
    """
    try:
        content = "\n".join([x for x in content.split("\n") if "WORKDIR" not in x])
    except:
        print(content)
        import IPython

        IPython.embed()

    global base_image_cache
    global empty_images
    global cache

    if use_cache and cache is None:
        cache = Cache()
        base_image_cache.update(cache.load())

    prompt = f"""
    You are a Dockerfile analyzer. Your task is to identify the software and system dependencies
    listed in the following Dockerfile.  Output a JSON object with the following keys:
    "base_image" for the base image, "software" (a list of strings), "devices" and "kernel"
    and be as comprehensive as possible, but **limit the JSON output to 10000 tokens, removing less
    relevant software if needed.  I only want JSON as the output, without any additional
    formatting or comment. Please keep software names to single strings, without spaces,
    all in lowercase, and use dashes if you need multiple words per string.
    If you know the package manager, please provide in the format <package-manager>:<software> and
    replace the bracketed terms with strings.

    Dockerfile:
    ```
    {content}
    ```
    """
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
    )

    # Let's have this raise for now
    response = model.generate_content(prompt)

    # When it was too complex (and couldn't generate json) this came back empty
    if not response.parts:
        print("👉 Response has no parts")
        if hasattr(response, "prompt_feedback") and response.prompt_feedback:
            raise ValueError(f"  Prompt Feedback: {response.prompt_feedback}")

    # We got a response?
    text = response.text.strip()

    # Attempt to parse the JSON - it comes back as either markdown or code blocks
    if text.startswith("```json"):
        text = text.strip()[7:-3].strip()
    elif text.startswith("```"):
        text = text.strip()[3:-3].strip()

    if not text:
        raise ValueError("Response has no text")
    try:
        # This will carry forward arch, etc.
        if metadata is not None:
            metadata.update(json.loads(text))
        else:
            metadata = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}\nResponse: {metadata}")

    # Look up base image - just assume one for now
    base_image = metadata.get("base_image")
    if not base_image:
        base_image = [x for x in content.split("\n") if "FROM" in x][0]
        if "$" in base_image:
            base_image = None

    # Cut out early if we won't get any metadata
    if not base_image or base_image in empty_images:
        return metadata

    if base_image not in base_image_cache and base_image not in empty_images:
        print(f"Looking for {base_image}")
        image = get_dockerfile(base_image, model_name)
        print(f"Image: {image}")
        if image is not None:
            base_image_cache[base_image] = image
            print(f"Base image cache: {base_image_cache}")

            # Save base image to cache. In case we recursed
            # into layers of images, save this at the top level
            image["uri"] = base_image
            if cache:
                cache.save(base_image, image)
        else:
            empty_images[base_image] = image
            print(f"Empty cache: {base_image_cache}")

    # Do we have it now?
    image = base_image_cache.get(base_image)
    if not image:
        return metadata

    # If we have it, use it to update
    for section in image:
        if section not in metadata and image[section]:
            metadata[section] = image[section]
        else:
            parent_section = image.get(section) or []
            image_section = metadata.get(section) or []
            metadata[section] = list(set(parent_section + image_section))

    # Cut out early if we won't get any metadata
    if "base_image" in metadata and isinstance(metadata["base_image"], list):
        del metadata["base_image"]
    return metadata


def get_dockerfile(image_name, model_name=defaults.model_name):
    """
    Fetches and parses the image configuration from a registry using skopeo.
    """
    crane_url = f"https://crane.ggcr.dev/config/{image_name}"
    response = requests.get(crane_url)

    # Let this error if it doesn't work
    try:
        config = response.json()
    except:
        raise ValueError(f"Cannot find config for {image_name}")

    # Save metadata and make a faux dockerfile to ask gemini about.
    # We usually can't get the FROM here, so we stop at this base image
    metadata = {"architecture": config["architecture"], "uri": image_name}
    dockerfile = ""

    # Environment variables can give the LLM hints to software, etc.
    cfg = config.get("config")
    for value in cfg.get("Env", []):
        dockerfile += f"ENV {value}\n"
    for key, value in cfg.get("Labels", {}).items():
        dockerfile += f"LABEL {key}={value}\n"
    command = cfg.get("Cmd")
    if command:
        dockerfile += f"CMD {command}"

    # Add layer run and workdir commands
    for layer in config["history"]:
        if layer.get("empty_layer") is True:
            continue
        if "created_by" not in layer:
            raise ValueError(f"Found image with empty layer: inspect:\n{layer}")
        line = layer["created_by"]
        if "WORKDIR" in line:
            continue
        dockerfile += line + "\n"

    # If we don't have any RUN we typically hit a from scratch image
    if "RUN" not in dockerfile:
        return
    return parse_dockerfile(content=dockerfile, model_name=model_name, metadata=metadata)
