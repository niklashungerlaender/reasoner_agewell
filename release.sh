#!/bin/bash

SD=$(cd $(dirname $0); pwd -P)
WD="`pwd`"
SCRIPT=$(basename $0)
SCRIPT_NAME=${SCRIPT%.*}
SCRIPT_EXTENSION=${SCRIPT##*.}
SELF=$SD/$SCRIPT

cd $SD/

export MAVEN_OPTS="-Xmx2048m -XX:+TieredCompilation -XX:TieredStopAtLevel=1"
mvnw release:clean release:prepare -Prelease $@
mvnw release:perform -Prelease $@

cd $WD/