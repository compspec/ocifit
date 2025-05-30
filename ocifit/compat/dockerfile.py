import json
import os

import requests

import ocifit.defaults as defaults


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
