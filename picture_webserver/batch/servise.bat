cd /d %~dp0
pushd ..\..\
set VENVBAT="C:\Users\%username%\Documents\python\env\picture_server\Scripts\activate.bat"
call %VENVBAT%
python -m picture_webserver.servise install
popd
pause