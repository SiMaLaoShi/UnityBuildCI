import os
import plistlib


class MobileProvisionData:
    def __init__(self):
        self.UUID = ""
        self.Name = ""
        self.TeamIdentifier = ""
        self.TeamName = ""


def parse_mobile_provision(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Mobile provision file not found.", file_path)

    r = open(file_path, 'rb')
    lines = r.readlines()
    start_index = None  # Initialize start index as None
    end_index = None  # Initialize end index as None

    # Find the line number with "<plist" at the beginning
    for i, line in enumerate(lines):
        if b'<plist' in line:
            start_index = i
            break

    # Find the line number with "</plist>" at the end
    for i, line in enumerate(lines[start_index:], start=start_index):
        if b'</plist>' in line:
            end_index = i
            break

    # Extract the content between start and end index and combine into a string
    content = b''.join(lines[start_index + 1:end_index]).decode('utf-8')
    content = '<plist version="1.0">\n' + content + '</plist>\n'
    print(content)

    try:
        dict_data = plistlib.loads(content.encode('utf-8'))
        if dict_data is not None:
            provision_data = MobileProvisionData()
            provision_data.UUID = dict_data.get('UUID')
            provision_data.TeamIdentifier = dict_data.get('TeamIdentifier')
            provision_data.TeamName = dict_data.get('TeamName')
            provision_data.Name = dict_data.get('Name')
            return provision_data

    except Exception as ex:
        raise Exception("Failed to parse mobile provision file.", ex)

    return None
