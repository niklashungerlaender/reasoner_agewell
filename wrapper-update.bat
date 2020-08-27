@ECHO OFF

SET WD=%CD%
SET SD=%~dp0
SET PARAMS=%*

cd "%SD%"

call mvnw -N io.takari:maven:LATEST:wrapper %PARAMS%

cd "%WD%"
