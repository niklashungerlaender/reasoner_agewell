@ECHO OFF

SET WD=%CD%
SET SD=%~dp0
SET PARAMS=%*

cd "%SD%"

call mvnw clean install -Pserver-deploy -Pagewell-server-deploy %PARAMS%

cd "%WD%"

PAUSE
