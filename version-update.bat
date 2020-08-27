@ECHO OFF

SET WD=%CD%
SET SD=%~dp0
SET PARAMS=%*

cd "%SD%"

set MAVEN_OPTS=-Xmx2048m -XX:+TieredCompilation -XX:TieredStopAtLevel=1
call mvnw -N versions:update-child-modules %PARAMS%
call mvnw versions:commit %PARAMS%

cd "%WD%"
