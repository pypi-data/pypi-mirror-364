#  net-device-conn

## Current Features 
- Still under development.

### How to Use:
    # Update pip and create a virtual environment, then activate the environment and install.
        ```
        python -m pip install --upgrade pip
        py -m venv venv
        .\venv\Scripts\activate
        python -m pip install .
        ```
    
    # If you have a GNS3 environment or a network device with SSH setup then you can try and connect to it.
        ```
        (venv) net-device-conn> python
        >>> import net_device_conn
        >>> handler = net_device_conn.DeviceHandler(device_type="cisco_ios", host='192.168.233.10', username='admin', password='cisco') 
        >>> h = handler.connect()
        >>> output = h.send_command('show ver')
        >>> print(output)
        >>> exit()
        ```

## Dependency:
    netmiko
