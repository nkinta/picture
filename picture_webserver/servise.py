from __future__ import print_function

from picture_webserver import server_main

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "FlaskApp"
    _svc_display_name_ = "FlaskApp"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        # !important! to report "SERVICE_STOPPED"
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        server_main.app.run(host='0.0.0.0', threaded=True, port=8080)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
