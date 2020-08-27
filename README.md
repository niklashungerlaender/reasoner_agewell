# Reasoner

This repository contains all necessary code to run the `Reasoner`


## CI

All the Python scripts in this repository (including *.ini and *.csv files) are packeged to a Debain-Package (*.deb) file utilizing the Gitlab CI features and Maven as build system.


## Server Deployment

To deploy a once buildt package to the preconfigured server, execute the `deploy-server` CI build-step.

After successful running the build-step login onto the server via SSH and execute:

`sudo dpkg -i /tmp/reasoner_0.0.1-SNAPSHOT_all.deb`

(maybe the file is slightly named different because the version changed)
