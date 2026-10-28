#!/usr/bin/env bash

# remove previous build files
make clean

# build multi-versioned documentation
sphinx-multiversion source build/html

# copy the default landing page
cp source/_static/html/default_landing.html build/html/index.html
