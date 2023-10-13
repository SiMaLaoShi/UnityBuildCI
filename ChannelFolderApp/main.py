import os
import sys

from PyQt5.QtCore import QFile, QTextStream, QSettings
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox

from parse_mobile_provision import parse_mobile_provision


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Channel Folder App")
        self.setGeometry(100, 100, 400, 250)

        self.label_channel_folder = QLabel("Channel Folder:", self)
        self.label_channel_folder.setGeometry(20, 20, 100, 20)

        self.entry_channel_folder = QLineEdit(self)
        self.entry_channel_folder.setGeometry(130, 20, 200, 20)

        self.btn_browse_channel_folder = QPushButton("Browse", self)
        self.btn_browse_channel_folder.setGeometry(340, 20, 50, 20)
        self.btn_browse_channel_folder.clicked.connect(self.browse_channel_folder)

        self.label_dev_mobileprovision = QLabel("Dev Mobile Provision:", self)
        self.label_dev_mobileprovision.setGeometry(20, 60, 100, 20)

        self.entry_dev_mobileprovision = QLineEdit(self)
        self.entry_dev_mobileprovision.setGeometry(130, 60, 200, 20)

        self.btn_browse_dev_mobileprovision = QPushButton("Browse", self)
        self.btn_browse_dev_mobileprovision.setGeometry(340, 60, 50, 20)
        self.btn_browse_dev_mobileprovision.clicked.connect(self.browse_dev_mobileprovision)

        self.label_dis_mobileprovision = QLabel("Dis Mobile Provision:", self)
        self.label_dis_mobileprovision.setGeometry(20, 100, 100, 20)

        self.entry_dis_mobileprovision = QLineEdit(self)
        self.entry_dis_mobileprovision.setGeometry(130, 100, 200, 20)

        self.btn_browse_dis_mobileprovision = QPushButton("Browse", self)
        self.btn_browse_dis_mobileprovision.setGeometry(340, 100, 50, 20)
        self.btn_browse_dis_mobileprovision.clicked.connect(self.browse_dis_mobileprovision)

        self.btn_process = QPushButton("Process", self)
        self.btn_process.setGeometry(150, 150, 100, 30)
        self.btn_process.clicked.connect(self.process_data)

        # Load last used folder paths
        settings = QSettings("YourCompany", "YourApp")
        last_channel_folder = settings.value("last_channel_folder", "")
        last_dev_mobileprovision = settings.value("last_dev_mobileprovision", "")
        last_dis_mobileprovision = settings.value("last_dis_mobileprovision", "")
        self.entry_channel_folder.setText(last_channel_folder)
        self.entry_dev_mobileprovision.setText(last_dev_mobileprovision)
        self.entry_dis_mobileprovision.setText(last_dis_mobileprovision)

    def save_last_used_paths(self):
        channel_folder = self.entry_channel_folder.text()
        dev_mobileprovision = self.entry_dev_mobileprovision.text()
        dis_mobileprovision = self.entry_dis_mobileprovision.text()

        # Save last used folder paths
        settings = QSettings("bc", "mobileprovision")
        settings.setValue("last_channel_folder", channel_folder)
        settings.setValue("last_dev_mobileprovision", dev_mobileprovision)
        settings.setValue("last_dis_mobileprovision", dis_mobileprovision)

    def browse_channel_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Channel Folder")
        self.entry_channel_folder.setText(folder_path)

    def browse_dev_mobileprovision(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Dev Mobile Provision", "", "Mobile Provision Files (*.mobileprovision)")
        self.entry_dev_mobileprovision.setText(file_path)

    def browse_dis_mobileprovision(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Dis Mobile Provision", "", "Mobile Provision Files (*.mobileprovision)")
        self.entry_dis_mobileprovision.setText(file_path)

    def save_string_to_file(self, string, folder_path):
        file_path = folder_path + "/ios.txt"

        file = QFile(file_path)
        if file.open(QFile.WriteOnly | QFile.Text):
            stream = QTextStream(file)
            stream << string
            file.close()
            QMessageBox.information(self, "Information", "String saved to file successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Failed to save string to file.")

    def process_data(self):
        channel_folder = self.entry_channel_folder.text()
        dev_mobileprovision = self.entry_dev_mobileprovision.text()
        dis_mobileprovision = self.entry_dis_mobileprovision.text()

        if channel_folder == "":
            QMessageBox.warning(self, "Warning", "Please enter the channel folder.")
            return False

        if dev_mobileprovision == "":
            QMessageBox.warning(self, "Warning", "Please enter the dev mobile provision.")
            return False

        if dis_mobileprovision == "":
            QMessageBox.warning(self, "Warning", "Please enter the dis mobile provision.")
            return False

        # channel_folder_path = os.path.abspath(channel_folder)
        # dev_mobileprovision_path = os.path.abspath(dev_mobileprovision)
        # dis_mobileprovision_path = os.path.abspath(dis_mobileprovision)
        #
        # if not dev_mobileprovision_path.startswith(channel_folder_path):
        #     QMessageBox.information(self, "错误提示", "mobileprovision文件必须要放到渠道下面")
        #     return
        #
        # if not dis_mobileprovision_path.startswith(channel_folder_path):
        #     QMessageBox.information(self, "错误提示", "mobileprovision文件必须要放到渠道下面")
        #     return

        # 在此处执行相应的操作，使用选择的路径进行处理
        dev = parse_mobile_provision(dev_mobileprovision)
        dis = parse_mobile_provision(dis_mobileprovision)

        sb = []
        sb.append("[debug]")
        sb.append(f"CODE_SIGN_IDENTITY={dev.TeamName}")
        sb.append(f"PROVISIONING_PROFILE={dev.UUID}")
        sb.append(f"PROVISIONING_PROFILE_SPECIFIER={dev.Name}")
        sb.append(f"DEVELOPMENT_TEAM={dev.TeamIdentifier}")
        sb.append("")

        sb.append("[release]")
        sb.append(f"CODE_SIGN_IDENTITY={dis.TeamName}")
        sb.append(f"PROVISIONING_PROFILE={dis.UUID}")
        sb.append(f"PROVISIONING_PROFILE_SPECIFIER={dis.Name}")
        sb.append(f"DEVELOPMENT_TEAM={dis.TeamIdentifier}")

        result = "\n".join(sb)
        print(result)

        self.save_string_to_file(result, channel_folder)

        # 示例：显示路径信息
        QMessageBox.information(self, "Path Information",
                                f"Channel Folder: {channel_folder}\n" +
                                f"Dev Mobile Provision: {dev_mobileprovision}\n" +
                                f"Dis Mobile Provision: {dis_mobileprovision}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())