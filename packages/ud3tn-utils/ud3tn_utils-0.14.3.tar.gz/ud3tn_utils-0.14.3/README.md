# python-uD3TN-utils

The Python package uD3TN-utils is a utility library to simplify the interaction
with the µD3TN daemon within python applications.

The included `AAP2Client` enables user-friendly communication with the µD3TN
daemon via local or remote sockets using the Application Agent Protocol 2 (AAP 2.0).
Besides sending and receiving bundles, it is also possible to change the
configuration of the µD3TN daemon via AAP messages.

## Installation

From source:

```sh
git clone https://gitlab.com/d3tn/ud3tn
pip install [-e] ud3tn/python-ud3tn-utils
```

From [PyPi](https://pypi.org/project/ud3tn-utils) directly:

```sh
pip install ud3tn-utils
```

## Development

For examples on the usage of this library, check out the contained CLI tools
in the `aap/bin` (for the old AAP v1 protocol) and `aap2/bin` (for AAP 2.0)
subdirectories.

python-uD3TN-utils is maintained as part of the µD3TN project and follows its
development processes. Please see the [µD3TN](https://gitlab.com/d3tn/ud3tn)
repository and [the µD3TN web documentation](https://d3tn.gitlab.io/ud3tn)
for further information.
