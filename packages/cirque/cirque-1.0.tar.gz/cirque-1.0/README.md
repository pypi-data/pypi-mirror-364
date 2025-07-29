# cirque
Communication Interface to Readout Electronics of QUantum Experiments
This repository provides a comfortable way of communication with the SDR-Systems developed by KIT-IPE.
It allows setting up the connection with the ipe-servicehub and abstracts the grpc-Calls for the endpoints.

## Important note
This package is only useful in combination with the Quantum Interface Controller hardware system developed at KIT-IPE.
This package is a wrapper around the python stubs auto-generated from the protobuf-messages. It is intended to offer a more user-friendly way of communicating with the Quantum Interface Controller Systems.

## Installation

To install `cirque` use

```shell
pip install cirque
```

### Local installation

> [!note]
> Local installation is only possible with access to the internal gitlab repository at gitlab.kit.edu

To install the package and make it available globally using `import cirque` globally, clone the repository and call
```shell
pip install -e .
```
from within this directory.


## Usage

The connection to the Quantum Interface Controller system can be set up as follows:

```shell
from cirque import servicehubutils

# Note: currently only IPv4 adresses are supported
platform_ip = "127.0.0.1"
con = servicehubutils.FPGAConnection(ip=platform_ip, port=50058)
```

the `con` object can now be used to communicate with the individual modules, as described in the documentation.

```shell
from cirque import pimc

# Instantiate platform information and management core
my_pimc = pimc.PIMC(con)
platform_ready = my_pimc.get_platform_ready()
```


## LICENSE
cirque is released under the terms of the **GNU General Public License** as published by the Free Software Foundation, either version 3 of the License, or any later version.
Please see the [COPYING](COPYING) files for details.
