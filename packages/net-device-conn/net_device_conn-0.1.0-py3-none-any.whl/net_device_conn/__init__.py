import netmiko
import logging

from net_device_conn.drivers.cisco import CiscoBase


class DeviceHandler:
    """
    A class to handle network device connections and operations using Netmiko.
    """
    def __init__(self,
                 host,
                 username,
                 password,
                 port=22,
                 secret='',
                 device_type="cisco_ios",
                 auto_connect=False):
        """
        Initializes the DeviceHandler with device connection parameters.

        Args:
            device_type (str): The type of the network device (e.g., 'cisco_ios').
            host (str): The IP address or hostname of the device.
            username (str): The username for device login.
            password (str): The password for device login.
            port (int, optional): The SSH port. Defaults to 22.
            secret (str, optional): The enable secret. Defaults to ''.
            auto_connect (bool, optional): Try to connect on init, else must call connect().
        """
        self.device_type = device_type
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.secret = secret
        self.connection = None
        if self.device_type == "cisco_ios":
            self.connection = CiscoBase(host=host, username=username, password=password, port=port, secret=secret)
        else:
            raise Exception(f"Unsupported device type: {self.device_type}")
        ## Auto connection
        if not self.connection and auto_connect == True:
            self.connect()

    def connect(self):
        """
        Establishes a connection to the network device.

        Returns:
            ConnectHandler: The Netmiko connection object.

        Raises:
            Exception: If the connection fails.
        """
        try:
            if self.connection:
                return self.connection

            device_params = {
                'device_type': self.device_type,
                'host': self.host,
                'username': self.username,
                'password': self.password,
                'port': self.port,
                'secret': self.secret
            }
            self.connection = netmiko.ConnectHandler(**device_params)
            return self.connection
        except Exception as e:
            raise Exception(f"Failed to connect to device: {e}")
        
        
    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None

    def send_command(self, command):
        if self.connection:
            return self.connection.send_command(command)
        else:
            raise Exception("Not connected to device")

    def send_config_set(self, config_commands):
        """
        Sends a set of configuration commands to the device.

        Args:
            config_commands (list): A list of configuration commands to send.

        Returns:
            str: The output of the configuration commands.

        Raises:
            Exception: If not connected to the device.
        """
        if self.connection:
            return self.connection.send_config_set(config_commands)
        else:
            raise Exception("Not connected to device")

    def send_command_timing(self, command, delay_factor=1):
        """
        Sends a command to the device and returns the output.

        Args:
            command (str): The command to send.
            delay_factor (int, optional): The delay factor for the command. Defaults to 1.

        Returns:
            str: The output of the command.

        Raises:
            Exception: If not connected to the device.
        """
        if self.connection:
            return self.connection.send_command_timing(command, delay_factor=delay_factor)
        else:
            raise Exception("Not connected to device")

    def send_multiline(self, command):
        if self.connection:
            return self.connection.send_multiline(command)
        else:
            raise Exception("Not connected to device")

    def find_prompt(self):
        if self.connection:
            return self.connection.find_prompt()
        else:
            raise Exception("Not connected to device")

    def save_config(self):
        if self.connection:
            return self.connection.save_config()
        else:
            raise Exception
    
    def file_transfer(self, source_file, dest_file, file_system, direction, **kwargs):
        """
        Transfers a file to or from the device.

        Args:
            source_file (str): The path to the source file.
            dest_file (str): The path to the destination file.
            file_system (str): The file system on the device (e.g., 'flash:').
            direction (str): 'put' to send to the device, 'get' to retrieve from the device.
            **kwargs: Additional keyword arguments to pass to the file_transfer function.

        Returns:
            bool: True if the transfer was successful, False otherwise.

        Raises:
            Exception: If not connected to the device.
        """
        if self.connection:
            return netmiko.file_transfer(
                self.connection,
                source_file=source_file,
                dest_file=dest_file,
                file_system=file_system,
                direction=direction,
                **kwargs
            )
        else:
            raise Exception("Not connected to device")
    
    def show_ver(self):
        return self.connection.show_ver()
