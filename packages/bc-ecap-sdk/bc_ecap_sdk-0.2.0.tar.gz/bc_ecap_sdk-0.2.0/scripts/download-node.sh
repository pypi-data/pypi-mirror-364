#!/bin/bash
set -e # Exit on error

DIST=../pkg
mkdir -p $DIST

echo "Downloading mac node"
curl -o $DIST/mac.node https://app.brainco.cn/universal/eeg-32ch/dist/v0.2.0/mac.node

echo "Downloading win node"
curl -o $DIST/win.node https://app.brainco.cn/universal/eeg-32ch/dist/v0.2.0/win.node
