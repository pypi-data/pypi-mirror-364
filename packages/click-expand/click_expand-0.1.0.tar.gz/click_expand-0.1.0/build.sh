#!/bin/bash

echo "# Building with flit:"
flit build

echo ""
echo "# Checking with twine:"
twine check dist/*

echo ""
echo "# Contents:"
tar -tzf dist/*.tar.gz
