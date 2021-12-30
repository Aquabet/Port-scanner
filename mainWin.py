import time
import socket
import sys
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, QRunnable, QObject
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from Ui_untitled import *


class mywindow(QMainWindow, Ui_MainWindow):
    signal = pyqtSignal(str)

    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.signal.connect(self.outResult)
        socket.setdefaulttimeout(0.5)

    def outResult(self, index):
        self.result.append(index)

    def clicked_scan(self):
        if self.radioButton_2.isChecked() == False and self.radioButton.isChecked() == False:
            QMessageBox.about(self, '警告', '请在ip地址和主机名中至少选择一个')
            return
        else:
            try:
                self.thread = int(self.threadNum.text())
            except ValueError:
                QMessageBox.about(self, '警告', '请输入正确的线程数，范围1~100')
                return
            if self.thread <= 0 or self.thread > 100:
                QMessageBox.about(self, '警告', '请输入正确的线程数，范围1~100')
                return

            try:
                socket1 = int(self.socket1.text())
                socket2 = int(self.socket2.text())
            except ValueError:
                QMessageBox.about(self, '警告', '请输入正确的端口范围，范围0~65535')
                return
            if (socket1 < 0 or socket1 > 65535) or (socket2 < 0 or socket2 > 65535) or (socket1 > socket2):
                QMessageBox.about(self, '警告', '请输入正确的端口范围，范围0~65535')
                return

            if self.radioButton.isChecked() == True:
                try:
                    muti = False
                    ip1 = int(self.ip1.text())
                    ip2 = int(self.ip2.text())
                    ip3 = int(self.ip3.text())
                    ip4 = int(self.ip4.text())
                    if self.ip5.text() != "":
                        muti = True
                        ip5 = int(self.ip5.text())
                except ValueError:
                    QMessageBox.about(self, '警告', '请输入正确的IP地址')
                    return
                if muti == False and ip1 >= 0 and ip1 <= 255 and ip2 >= 0 and ip2 <= 255 and ip3 >= 0 and ip3 <= 255 and ip4 >= 0 and ip4 <= 255:
                    self.host = []
                    self.portbegin = socket1
                    self.portend = socket2
                    self.host.append(str(ip1)+"."+str(ip2) +
                                     "." + str(ip3)+"."+str(ip4))
                    self.scan()
                elif muti == True and ip1 >= 0 and ip1 <= 255 and ip2 >= 0 and ip2 <= 255 and ip3 >= 0 and ip3 <= 255 and ip4 >= 0 and ip4 <= 255 and ip5 >= 0 and ip5 <= 255 and ip4 < ip5:
                    self.host = []
                    self.portbegin = socket1
                    self.portend = socket2
                    for i in range(ip4, ip5+1):
                        self.host.append(
                            str(ip1)+"."+str(ip2) + "."+str(ip3)+"."+str(i))
                    self.scan()
                else:
                    QMessageBox.about(self, '警告', '请输入正确的IP地址')
                    return
            else:
                if self.hostname.text() == "":
                    QMessageBox.about(self, '警告', '请输入主机名')
                    return
                try:
                    hostip = socket.gethostbyname(self.hostname.text())
                except socket.gaierror:
                    QMessageBox.about(self, '警告', '请输入正确的主机名')
                    return
                self.result.append("Begin working")
                self.host = [hostip]
                self.scan()

    def scan(self):
        self.signal.emit("Start scaning")
        self.taskthread = TasksThread(
            self.host, self.portbegin, self.portend, self.signal, self.thread)
        self.taskthread.start()

    def clicked_clear(self):
        self.result.clear()

    def clicked_exit(self):
        QApplication.instance().exit()
        # exit()


class TasksThread(QThread):
    def __init__(self, host, portbegin, portend, signal, thread_count):
        super(TasksThread, self).__init__()
        self.host = host
        self.portbegin = portbegin
        self.portend = portend
        self.signal = signal
        self.thread_count = thread_count
        self.task = Tasks(host, portbegin, portend, signal, thread_count)

    def run(self):
        self.task.start()


class Tasks(QObject):
    def __init__(self, host, portbegin, portend, signal, thread_count):
        super(Tasks, self).__init__()
        self.host = host
        self.portbegin = portbegin
        self.portend = portend
        self.signal = signal
        self.thread_count = thread_count
        self.pool = QThreadPool()
        self.pool.globalInstance()

    def start(self):
        self.pool.setMaxThreadCount(self.thread_count)
        time1 = time.time()
        for ip in self.host:
            for port in range(self.portbegin, self.portend+1):
                thread_ins = MyThread()
                thread_ins.setAutoDelete(True)
                thread_ins.transfer(ip=ip, port=port, signal=self.signal)
                self.pool.start(thread_ins)
        self.pool.waitForDone()
        time2 = time.time()
        self.signal.emit("Finish, spending %.3f s" % (time2-time1))

class MyThread(QRunnable):
    def __init__(self):
        super(MyThread, self).__init__()

    def transfer(self, ip="", port=0, signal=None):
        self.ip = ip
        self.port = port
        self.signal = signal

    def run(self):
        s = socket.socket(2, 1)
        res = s.connect_ex((self.ip, self.port))
        if res == 0:
            self.signal.emit('{0} port {1} is open'.format(self.ip, self.port))
        s.close()
        # server = telnetlib.Telnet()
        # try:
        #     server.open(self.ip, self.port)
        #     self.signal.emit(
        #         '{0} port {1} is open'.format(self.ip, self.port))
        # except Exception as err:
        #     self.signal.emit(
        #         '{0} port {1} is not open'.format(self.ip, self.port))
        #     pass
        # finally:
        #     server.close()


app = QtWidgets.QApplication(sys.argv)
myshow = mywindow()
myshow.show()
sys.exit(app.exec_())
