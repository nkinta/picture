cd /d %~dp0
pushd ..\..\
set PATH="C:\Program Files\Python36\";%PATH%
python -m picture_webserver.servise start
popd
pause