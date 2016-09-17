#!/usr/bin/env bash

sphinx-apidoc -f -o source ../ 
make html
