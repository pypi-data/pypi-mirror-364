from netmiko.f5.f5_tmsh_ssh import F5TmshSSH

class F5Base(F5TmshSSH):
    """
    Overloads the Netmiko F5TmshSSH class to provide additional functionality.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_command(self, command_string, **kwargs):
        """
        Sends a command to the F5 device.

        Args:
            command_string (str): The command to send.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The output of the command.
        """
        return super().send_command(command_string, **kwargs)

    def send_config_set(self, config_commands=None, **kwargs):
        """
        Sends a set of configuration commands to the F5 device.

        Args:
            config_commands (list): A list of configuration commands to send.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The output of the configuration commands.
        """
        return super().send_config_set(config_commands, **kwargs)

    def save_config(self, cmd="save sys config", **kwargs):
        """
        Saves the running configuration to the startup configuration.

        Args:
            cmd (str): The command to save the configuration.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The output of the save command.
        """
        return super().send_command(cmd, **kwargs)
