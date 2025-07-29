# uvartage

_A wrapper around **uv** for usage with artifact storage in airgapped environments_

So far only artifactory is supported as artifact storage backend yet.

## Prerequisites

[uv](https://docs.astral.sh/uv/) has to be installed,
but otherwise, only standard library modules are used.


## Usage

```console
[osuser@workstation workdir]$ PYTHONPATH=src python3 -m uvartage --help
usage: uvartage [-h] [--version] [-v ] [--backend {artifactory}] [--ca-file CA_FILE] [--user USER]
                [USER@]HOSTNAME ...

Wrapper for uv with artifact storage in airgapped environments

positional arguments:
  [USER@]HOSTNAME       the artifact storage hostname, or user and hostname combined by '@'.
  repositories          the package repositories (default first). If not at least one repository name
                        is provided, the value of the environment variable UVARTAGE_DEFAULT_REPOSITORY
                        will be used.

options:
  -h, --help            show this help message and exit
  --version             print version and exit
  -v , --verbose        show more messages
  --backend {artifactory}
                        the artifact storage backend type (default and currently the only supported
                        backend: artifactory)
  --ca-file CA_FILE     a CA cert bundle file to be provided via SSL_CERT_FILE.
  --user USER           username for the artifact storage backend if the hostname is not explicitly
                        specified as USER@HOSTNAME; default is 'osuser'.

[osuser@workstation workdir]$
```
