import re
import logging
from netmiko.cisco.cisco_ios import CiscoIosBase

class CiscoBase(CiscoIosBase):
    """
    Overloads the Netmiko CiscoIosBase class to provide additional functionality.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_command(self, command_string, **kwargs):
        """
        Sends a command to the Cisco device.

        Args:
            command_string (str): The command to send.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The output of the command.
        """
        return super().send_command(command_string, **kwargs)

    def send_config_set(self, config_commands=None, **kwargs):
        """
        Sends a set of configuration commands to the Cisco device.

        Args:
            config_commands (list): A list of configuration commands to send.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The output of the configuration commands.
        """
        return super().send_config_set(config_commands, **kwargs)

    def save_config(self, cmd="write memory", **kwargs):
        """
        Saves the running configuration to the startup configuration.

        Args:
            cmd (str): The command to save the configuration.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The output of the save command.
        """
        return super().send_command(cmd, **kwargs)
    
    def show_ver(self):
        output = super().send_command('show version')
        logging.info("output of show_ver")
        parsed_output = re.search('.*,\\sVersion(.*),', output).group(1).strip()
        return parsed_output
