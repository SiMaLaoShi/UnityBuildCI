import os
import sys

from PyQt5.QtCore import QSettings, QFile, QTextStream
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QGridLayout, QWidget, \
    QFileDialog, QMessageBox

from parse_mobile_provision import parse_mobile_provision


def get_relative_path(folder1, folder2):
    return os.path.relpath(folder2, folder1).replace("\\", "/")


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IOS Txt Editor")
        self.setGeometry(100, 100, 800, 250)

        grid_layout = QGridLayout()

        # App Id
        self.label_app_id = QLabel("App Id:")
        self.entry_app_id = QLineEdit()
        grid_layout.addWidget(self.label_app_id, 0, 0)
        grid_layout.addWidget(self.entry_app_id, 0, 1)

        # App Name
        self.label_app_name = QLabel("App Name:")
        self.entry_app_name = QLineEdit()
        grid_layout.addWidget(self.label_app_name, 1, 0)
        grid_layout.addWidget(self.entry_app_name, 1, 1)

        # Mac Password
        self.label_mac_pwd = QLabel("Mac Password:")
        self.entry_mac_pwd = QLineEdit()
        grid_layout.addWidget(self.label_mac_pwd, 2, 0)
        grid_layout.addWidget(self.entry_mac_pwd, 2, 1)

        # P12 Password
        self.label_p12_pwd = QLabel("P12 Password:")
        self.entry_p12_pwd = QLineEdit()
        grid_layout.addWidget(self.label_p12_pwd, 3, 0)
        grid_layout.addWidget(self.entry_p12_pwd, 3, 1)

        # Channel Folder
        self.label_channel_folder = QLabel("Channel Folder:")
        self.entry_channel_folder = QLineEdit()
        self.btn_browse_channel_folder = QPushButton("Browse")
        self.btn_browse_channel_folder.clicked.connect(self.browse_channel_folder)
        grid_layout.addWidget(self.label_channel_folder, 4, 0)
        grid_layout.addWidget(self.entry_channel_folder, 4, 1)
        grid_layout.addWidget(self.btn_browse_channel_folder, 4, 2)

        # Dev P12
        self.label_dev_p12 = QLabel("Dev P12:")
        self.entry_dev_p12 = QLineEdit()
        self.btn_browse_dev_p12 = QPushButton("Browse")
        self.btn_browse_dev_p12.clicked.connect(self.browse_dev_p12)
        grid_layout.addWidget(self.label_dev_p12, 5, 0)
        grid_layout.addWidget(self.entry_dev_p12, 5, 1)
        grid_layout.addWidget(self.btn_browse_dev_p12, 5, 2)

        # Dis P12
        self.label_dis_p12 = QLabel("Dis P12:")
        self.entry_dis_p12 = QLineEdit()
        self.btn_browse_dis_p12 = QPushButton("Browse")
        self.btn_browse_dis_p12.clicked.connect(self.browse_dis_p12)
        grid_layout.addWidget(self.label_dis_p12, 6, 0)
        grid_layout.addWidget(self.entry_dis_p12, 6, 1)
        grid_layout.addWidget(self.btn_browse_dis_p12, 6, 2)

        # Dev Cer
        self.label_dev_cer = QLabel("Dev Cer:")
        self.entry_dev_cer = QLineEdit()
        self.btn_browse_dev_cer = QPushButton("Browse")
        self.btn_browse_dev_cer.clicked.connect(self.browse_dev_cer)
        grid_layout.addWidget(self.label_dev_cer, 7, 0)
        grid_layout.addWidget(self.entry_dev_cer, 7, 1)
        grid_layout.addWidget(self.btn_browse_dev_cer, 7, 2)

        # Dis Cer
        self.label_dis_cer = QLabel("Dis Cer:")
        self.entry_dis_cer = QLineEdit()
        self.btn_browse_dis_cer = QPushButton("Browse")
        self.btn_browse_dis_cer.clicked.connect(self.browse_dis_cer)
        grid_layout.addWidget(self.label_dis_cer, 8, 0)
        grid_layout.addWidget(self.entry_dis_cer, 8, 1)
        grid_layout.addWidget(self.btn_browse_dis_cer, 8, 2)

        # Dev Mobile Provision
        self.label_dev_mobileprovision = QLabel("Dev Mobile Provision:")
        self.entry_dev_mobileprovision = QLineEdit()
        self.btn_browse_dev_mobileprovision = QPushButton("Browse")
        self.btn_browse_dev_mobileprovision.clicked.connect(self.browse_dev_mobileprovision)
        grid_layout.addWidget(self.label_dev_mobileprovision, 9, 0)
        grid_layout.addWidget(self.entry_dev_mobileprovision, 9, 1)
        grid_layout.addWidget(self.btn_browse_dev_mobileprovision, 9, 2)

        # Dis Mobile Provision
        self.label_dis_mobileprovision = QLabel("Dis Mobile Provision:")
        self.entry_dis_mobileprovision = QLineEdit()
        self.btn_browse_dis_mobileprovision = QPushButton("Browse")
        self.btn_browse_dis_mobileprovision.clicked.connect(self.browse_dis_mobileprovision)
        grid_layout.addWidget(self.label_dis_mobileprovision, 10, 0)
        grid_layout.addWidget(self.entry_dis_mobileprovision, 10, 1)
        grid_layout.addWidget(self.btn_browse_dis_mobileprovision, 10, 2)

        # Operation Button
        self.btn_operation = QPushButton("Perform Operation")
        self.btn_operation.clicked.connect(self.perform_operation)
        grid_layout.addWidget(self.btn_operation, 11, 0, 1, 3)

        # Load last used folder paths
        settings = QSettings("eaw", "ChannelFolderApp")
        self.entry_channel_folder.setText(settings.value("last_channel_folder", ""))
        self.entry_dev_mobileprovision.setText(settings.value("last_dev_mobileprovision", ""))
        self.entry_dis_mobileprovision.setText(settings.value("last_dis_mobileprovision", ""))
        self.entry_app_id.setText(settings.value("last_app_id", ""))
        self.entry_app_name.setText(settings.value("last_app_name", ""))
        self.entry_mac_pwd.setText(settings.value("last_mac_pwd", ""))
        self.entry_p12_pwd.setText(settings.value("last_p12_pwd", ""))
        self.entry_dev_p12.setText(settings.value("last_dev_p12", ""))
        self.entry_dis_p12.setText(settings.value("last_dis_p12", ""))
        self.entry_dev_cer.setText(settings.value("last_dev_cer", ""))
        self.entry_dis_cer.setText(settings.value("last_dis_cer", ""))

        widget = QWidget()
        widget.setLayout(grid_layout)
        self.setCentralWidget(widget)

    def save_last_used_paths(self):
        channel_folder = self.entry_channel_folder.text()
        dev_mobileprovision = self.entry_dev_mobileprovision.text()
        dis_mobileprovision = self.entry_dis_mobileprovision.text()
        app_id = self.entry_app_id.text()
        app_name = self.entry_app_name.text()
        mac_pwd = self.entry_mac_pwd.text()
        p12_pwd = self.entry_p12_pwd.text()
        dev_p12 = self.entry_dev_p12.text()
        dis_p12 = self.entry_dis_p12.text()
        dev_cer = self.entry_dev_cer.text()
        dis_cer = self.entry_dis_cer.text()

        # Save last used folder paths
        settings = QSettings("eaw", "ChannelFolderApp")
        settings.setValue("last_channel_folder", channel_folder)
        settings.setValue("last_dev_mobileprovision", dev_mobileprovision)
        settings.setValue("last_dis_mobileprovision", dis_mobileprovision)
        settings.setValue("last_app_id", app_id)
        settings.setValue("last_app_name", app_name)
        settings.setValue("last_mac_pwd", mac_pwd)
        settings.setValue("last_p12_pwd", p12_pwd)
        settings.setValue("last_dev_p12", dev_p12)
        settings.setValue("last_dis_p12", dis_p12)
        settings.setValue("last_dev_cer", dev_cer)
        settings.setValue("last_dis_cer", dis_cer)

    def browse_channel_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Channel Folder")
        self.entry_channel_folder.setText(folder)

    def browse_dev_p12(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Dev P12", "", "Mobile P12 (*.p12)")
        self.entry_dev_p12.setText(file)

    def browse_dis_p12(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Dis P12", "", "Mobile P12 (*.p12)")
        self.entry_dis_p12.setText(file)

    def browse_dev_cer(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Dev Cer", "", "Mobile Cer (*.cer)")
        self.entry_dev_cer.setText(file)

    def browse_dis_cer(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Dis Cer", "", "Mobile Cer (*.cer)")
        self.entry_dis_cer.setText(file)

    def browse_dev_mobileprovision(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Dev Mobile Provision", "", "Mobile Provision Files (*.mobileprovision)")
        self.entry_dev_mobileprovision.setText(file)

    def browse_dis_mobileprovision(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Dis Mobile Provision", "", "Mobile Provision Files (*.mobileprovision)")
        self.entry_dis_mobileprovision.setText(file)

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

    def perform_operation(self):
        self.save_last_used_paths()
        # Retrieve entered values
        app_id = self.entry_app_id.text()
        app_name = self.entry_app_name.text()
        mac_pwd = self.entry_mac_pwd.text()
        p12_pwd = self.entry_p12_pwd.text()
        dev_p12 = self.entry_dev_p12.text()
        dis_p12 = self.entry_dis_p12.text()
        dev_cer = self.entry_dev_cer.text()
        dis_cer = self.entry_dis_cer.text()

        channel_folder = self.entry_channel_folder.text()
        dev_mobileprovision = self.entry_dev_mobileprovision.text()
        dis_mobileprovision = self.entry_dis_mobileprovision.text()

        if not all([app_id, app_name, mac_pwd, p12_pwd, dev_p12, dis_p12, dev_cer, dis_cer]):
            QMessageBox.warning(self, "Warning", "Error: One or more parameters are empty.")
            return False

        if channel_folder == "":
            QMessageBox.warning(self, "Warning", "Please enter the channel folder.")
            return False

        if dev_mobileprovision == "":
            QMessageBox.warning(self, "Warning", "Please enter the dev mobile provision.")
            return False

        if dis_mobileprovision == "":
            QMessageBox.warning(self, "Warning", "Please enter the dis mobile provision.")
            return False

        channel_folder_path = os.path.abspath(channel_folder)
        dev_mobileprovision_path = os.path.abspath(dev_mobileprovision)
        dis_mobileprovision_path = os.path.abspath(dis_mobileprovision)

        if not dev_mobileprovision_path.startswith(channel_folder_path):
            QMessageBox.information(self, "错误提示", "mobileprovision文件必须要放到渠道下面")
            return

        if not dis_mobileprovision_path.startswith(channel_folder_path):
            QMessageBox.information(self, "错误提示", "mobileprovision文件必须要放到渠道下面")
            return

        # 在此处执行相应的操作，使用选择的路径进行处理
        dev = parse_mobile_provision(dev_mobileprovision)
        dis = parse_mobile_provision(dis_mobileprovision)

        sb = []
        sb.append("[app]")
        sb.append(f"appId={app_id}")
        sb.append(f"appName={app_name}")
        sb.append(f"teamId={dis.TeamIdentifier[0]}")
        sb.append(f"dev_profile_id={dev.Name}")
        sb.append(f"dis_profile_id={dis.Name}")
        sb.append("")

        sb.append("[p12]")
        sb.append(f"macPwd={mac_pwd}")
        sb.append(f"p12Pwd={p12_pwd}")
        sb.append(f"devP12={get_relative_path(channel_folder, dev_p12)}")
        sb.append(f"disP12={get_relative_path(channel_folder, dis_p12)}")
        sb.append(f"devMob={get_relative_path(channel_folder, dev_mobileprovision)}")
        sb.append(f"devUUID={dev.UUID}")
        sb.append(f"disMob={get_relative_path(channel_folder, dis_mobileprovision)}")
        sb.append(f"disUUID={dis.UUID}")
        sb.append(f"devCer={get_relative_path(channel_folder, dev_cer)}")
        sb.append(f"disCer={get_relative_path(channel_folder, dis_cer)}")
        sb.append("")

        sb.append("[debug]")
        sb.append(f"CODE_SIGN_IDENTITY={dev.TeamName}")
        sb.append(f"PROVISIONING_PROFILE={dev.UUID}")
        sb.append(f"PROVISIONING_PROFILE_SPECIFIER={dev.Name}")
        sb.append(f"DEVELOPMENT_TEAM={dev.TeamIdentifier[0]}")
        sb.append("")

        sb.append("[release]")
        sb.append(f"CODE_SIGN_IDENTITY={dis.TeamName}")
        sb.append(f"PROVISIONING_PROFILE={dis.UUID}")
        sb.append(f"PROVISIONING_PROFILE_SPECIFIER={dis.Name}")
        sb.append(f"DEVELOPMENT_TEAM={dis.TeamIdentifier[0]}")

        result = "\n".join(sb)
        print(result)

        self.save_string_to_file(result, channel_folder)

        # 示例：显示路径信息
        QMessageBox.information(self, "Path Information",
                                f"Channel Folder: {channel_folder}\n" +
                                f"Dev Mobile Provision: {dev_mobileprovision}\n" +
                                f"Dis Mobile Provision: {dis_mobileprovision}")

        print("Operation performed!")


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())