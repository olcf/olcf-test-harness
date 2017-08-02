#!/usr/bin/env bash

sphinx-apidoc -f -o source ../harness_source_documentation
make html
