#!/bin/bash
VERSION="0.2.0"
URL="https://get.adc-connect.org/pyadcman/$VERSION/pyadcman.cpython-36m-x86_64-linux-gnu.so"
wget --user "$USER" --password "$PYADCMAN_PASSWORD" "$URL"
