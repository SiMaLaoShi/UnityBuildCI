import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address, server_window):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server_window = server_window

    def run(self):
        self.server_window.print_log(f'Client connected: {self.client_address}')

        while True:
            try:
                data = self.client_socket.recv(1024).decode().strip()
                if not data:
                    break

                self.server_window.print_log(f'Received from {self.client_address}: {data}')

                # Process the received command (implement your logic here)
                response = self.process_command(data)

                self.server_window.print_log(f'Sending response to {self.client_address}: {response}')

                self.client_socket.sendall(response.encode())
            except socket.error as e:
                self.server_window.print_log(f'Error with client {self.client_address}: {str(e)}')
                break

        self.client_socket.close()
        self.server_window.print_log(f'Client disconnected: {self.client_address}')

    def process_command(self, command):
        # Implement your command processing logic here
        # This is a sample implementation that echoes the command back to the client
        return command


class ServerSignals(QObject):
    log_updated = pyqtSignal(str)


class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Server')
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 10, 780, 540)
        self.text_edit.setReadOnly(True)

        self.server_socket = None
        self.client_threads = []

        self.signals = ServerSignals()

        self.signals.log_updated.connect(self.print_log)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8002))
        self.server_socket.listen(5)
        self.print_log('Server started. Listening on port 8002...')

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                thread = ClientThread(client_socket, client_address, self)
                thread.start()
                self.client_threads.append(thread)
            except socket.error as e:
                self.print_log(f'Error with client connection: {str(e)}')

    def print_log(self, message):
        self.text_edit.append(message)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', 'Are you sure you want to exit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.server_socket:
                self.server_socket.close()
            for thread in self.client_threads:
                thread.join()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())