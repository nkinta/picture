pushd ..\..\
set VENVBAT="C:\Users\%username%\Documents\python\env\picture_server\Scripts\activate.bat"
call %VENVBAT%
python -m picture_webserver.server_main
popd
pause