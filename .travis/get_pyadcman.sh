#!/bin/bash
VERSION="0.0.0"
URL="https://get.adc-connect.org/pyadcman/$VERSION/pyadcman.cpython-35m-x86_64-linux-gnu.so"
wget --user "$USER" --password "$PYADCMAN_PASSWORD" "$URL"
