def get_parser(name):
    Parser = None
    if name == "software":
        from .software import SoftwareParser as Parser
    elif name == "nfd":
        from .nfd import NFDParser as Parser
    if not Parser:
        raise ValueError(f"{name} is not a known parser.")
    return Parser
