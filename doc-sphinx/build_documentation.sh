#!/usr/bin/env bash

sphinx-apidoc -f -o source ../test/
make html
