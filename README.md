# ocifit

> Determine if a container is fit for an environment using OCI artifacts

[![PyPI version](https://badge.fury.io/py/ocifit.svg)](https://badge.fury.io/py/ocifit)

This tool is intended for the HPC community to assess the fit of an application container to a cloud environment.

## Design

We want to:

1. Generate compatibility artifacts for a set of containers (from Dockerfile or URI).
2. Generate [node feature groups](https://kubernetes-sigs.github.io/node-feature-discovery/v0.17/usage/customization-guide.html#nodefeaturegroup-custom-resource) that can describe nodes in an HPC cluster, or a Kubernetes cluster.
3. Assess how well a set of containers matches a node feature group
4. Return a recommended list.

To start, I will use the Gemini API to take a Dockerfile or container URI and go up one level (parent) to derive software.

## Development

Install dependencies and shell in:

```bash
pixi install
pixi shell
```

And export your `GEMINI_TOKEN`

```bash
export GEMINI_TOKEN=xxxxxxxxx
```

Then test against an image, optionally adding a uri to include.

```bash
ocifit compat --uri ghcr.io/converged-computing/lammps-reax:ubuntu2204 ./Dockerfile
```

Try using a different parser:

```bash
ocifit compat --uri ghcr.io/converged-computing/lammps-reax:ubuntu2204 ./Dockerfile --parser nfd
```

Also try adding one or more `--path` to an executable to run ldd against and provide links in the compatibility spec.

```bash
ocifit compat --uri ghcr.io/converged-computing/lammps-reax:ubuntu2204 ./Dockerfile --parser nfd --path /usr/bin/lmp
```

By default, parsed parent images are saved to a cache in `~/.ocifit`. If you add `--save` and provide a URI with `--uri`, your image will be as well. Note that this currently doesn't parse into a proper artifact because we still need to think about how the key/value pairs will work.

 - [see example for lammps-reax](examples/lammps-reax.json)

## License

HPCIC DevTools is distributed under the terms of the MIT license.
All new contributions must be made under this license.

See [LICENSE](https://github.com/converged-computing/cloud-select/blob/main/LICENSE),
[COPYRIGHT](https://github.com/converged-computing/cloud-select/blob/main/COPYRIGHT), and
[NOTICE](https://github.com/converged-computing/cloud-select/blob/main/NOTICE) for details.

SPDX-License-Identifier: (MIT)

LLNL-CODE- 842614
