__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2025, Vanessa Sochat"
__license__ = "MIT"

import json
import os

import ocifit.utils as utils

from ..compat import CompatGenerator


def main(args, parser, extra, subparser):

    # Set defaults
    args.outdir = args.outdir or os.getcwd()
    outfile = None

    print("          save: %s" % args.save)
    print("         image: %s" % args.image)
    print("      no-cache: %s" % args.no_cache)

    # We don't require the user to provide these
    if args.uri:
        print("           uri: %s" % args.uri)
    if args.outdir:
        print("        outdir: %s" % args.outdir)
    if args.outfile:
        print("       outfile: %s" % args.outfile)

    cli = CompatGenerator(args.parser, use_cache=not args.no_cache)
    compat = cli.generate(
        args.image,
        model_name=args.model_name,
        save=args.save,
        uri=args.uri,
        paths=args.path,
        pattern=args.pattern,
    )

    # If we don't have a file and we have a URI, save to cache.
    # Default to using outfile first, then outdir if defined
    if args.outfile:
        outfile = args.outfile
    if outfile and args.outdir:
        outfile = os.path.join(args.outdir, "%s.json" % cli.save_path(args.image))
        dirname = os.path.dirname(outfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    # If we have an output file, make sure to set step output
    if outfile:
        print(f"Saving to {outfile}...")
        utils.write_json(compat, outfile)
    else:
        print(json.dumps(compat, indent=4))
