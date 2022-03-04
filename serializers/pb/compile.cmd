@echo off

echo compiling proto buffer files for Python now

rem protoc --go_out=plugins=grpc:../services/ *.proto
python -m grpc_tools.protoc --python_out=../ --grpc_python_out=../ -I. *.proto
