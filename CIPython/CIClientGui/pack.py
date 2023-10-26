import datetime

from PyQt5.QtCore import QTimer, QProcess, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QLabel, QComboBox, QLineEdit
import sys
import tail
from packthread import PackThread


def on_process_finished(exit_code, exit_status):
    print(f"on_process_finished{exit_code} {exit_status}")


class MainWindow(QMainWindow):
    def __init__(self, unity_path, project_path):
        super().__init__()

        self.unity_path = unity_path
        self.project_path = project_path

        self.build_button = QPushButton("Build", self)
        self.build_button.setGeometry(50, 50, 200, 50)
        self.build_button.clicked.connect(self.execute_build_command)

        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setGeometry(50, 120, 800, 400)
        self.log_text_edit.setReadOnly(True)

        self.open_log_button = QPushButton("Open Log", self)
        self.open_log_button.setGeometry(50, 540, 100, 40)
        self.open_log_button.clicked.connect(self.open_log_file)
        self.open_log_button.setEnabled(False)

        version_label = QLabel("Version:", self)
        version_label.setGeometry(300, 50, 100, 30)

        self.version_line_edit = QLineEdit(self)
        self.version_line_edit.setText("1.0")

        self.version_line_edit.setGeometry(400, 50, 200, 30)

        channel_label = QLabel("Channel:", self)
        channel_label.setGeometry(300, 90, 100, 30)

        self.channel_line_edit = QLineEdit(self)
        self.channel_line_edit.setGeometry(400, 90, 200, 30)
        self.channel_line_edit.setText("001")

        export_method_label = QLabel("Export Method:", self)
        export_method_label.setGeometry(650, 50, 100, 30)

        self.export_method_combo = QComboBox(self)
        self.export_method_combo.setGeometry(750, 50, 100, 30)
        self.export_method_combo.addItems(["development", "app-store"])

        platform_label = QLabel("Platform:", self)
        platform_label.setGeometry(650, 90, 100, 30)

        self.platform_combo = QComboBox(self)
        self.platform_combo.setGeometry(750, 90, 100, 30)
        self.platform_combo.addItems(["ios", "android"])

        self.log_thread = None
        self.tail_thread = None
        self.log_path = None

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.check_process_timeout)
        # self.timer.start(10000)  # 设置超时时间为60秒

    def open_log_file(self):
        if self.log_path is not None:
            url = QUrl.fromLocalFile(self.log_path)
            QDesktopServices.openUrl(url)

    def check_process_timeout(self):
        if self.log_thread.state() == QProcess.Running:
            print("Process timeout. Killing process.")
            self.log_thread.kill()
            self.tail_thread.stop()
            self.build_button.setEnabled(True)

    def execute_build_command(self):
        self.log_text_edit.clear()
        # 格式化为字符串，按指定格式输出
        self.log_path = f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}_unity_log.log"
        if self.log_thread is not None:
            self.log_thread.terminate()
            self.log_thread = None
        if self.tail_thread is not None:
            self.tail_thread.stop()
        version = self.version_line_edit.text()
        channel = self.channel_line_edit.text()
        export_method = self.export_method_combo.currentText()
        platform = self.platform_combo.currentText()
        self.log_thread = PackThread(unity_path, project_path, self.log_path, version, channel, export_method, platform)
        self.log_thread.finished.connect(self.on_process_finished)
        print(f"抓取log {self.log_path}")
        self.tail_thread = tail.Tail(self.log_path)
        self.log_thread.start()
        self.tail_thread.logger.log_received.connect(self.append_log)
        self.tail_thread.start()
        self.build_button.setEnabled(False)
        self.open_log_button.setEnabled(True)

    # 定义要执行的函数
    def on_process_finished(self):
        self.build_button.setEnabled(True)
        self.log_thread.terminate()
        self.tail_thread.stop()
        self.append_log("打包结束!!!!")

    def append_log(self, log):
        self.log_text_edit.append(log)
        self.log_text_edit.ensureCursorVisible()

    def closeEvent(self, event):
        self.log_thread.terminate()
        self.tail_thread.stop()
        event.accept()


if __name__ == "__main__":
    # https: // docs.unity3d.com / cn / 2018.4 / Manual / CommandLineArguments.html
    unity_path = "D:/Uni/20200348/Editor/Unity.exe"  # 替换为你的Unity可执行文件路径
    project_path = "D:/GitHub/BuildCI"  # 替换为你的Unity项目路径

    app = QApplication(sys.argv)
    window = MainWindow(unity_path, project_path)
    window.resize(1000, 600)  # 设置窗口尺寸
    window.show()
    sys.exit(app.exec_())
