from PyQt5.QtCore import QProcess, QThread, pyqtSignal


class PackThread(QThread):
    log_received = pyqtSignal(str)

    def __init__(self, unity_path, project_path, log_path, version, channel, export_method, platform):
        super().__init__()
        self.unity_path = unity_path
        self.project_path = project_path
        self.log_path = log_path
        self.version = version
        self.channel = channel
        self.export_method = export_method
        self.platform = platform

    def run(self):
        command = [
            self.unity_path,
            "-quit",
            "-projectPath",
            self.project_path,
            "-batchmode",
            "-executeMethod",
            "BuildPip.Pack",
            f"-Version {self.version} -Channel {self.channel} -ExportMethod {self.export_method} -Platform {self.platform}",
            '-logFile',
            self.log_path
        ]
        print(f"执行打包{''.join(command)}")
        process = QProcess()
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.start(command[0], command[1:])
        process.waitForFinished(-1)