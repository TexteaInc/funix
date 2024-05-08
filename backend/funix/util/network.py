"""
Network utils for funix.
"""

from ipaddress import IPv4Address, IPv6Address
from socket import AF_INET, SOCK_STREAM, socket


def get_compressed_ip_address_as_str(host: IPv4Address | IPv6Address) -> str:
    """
    Get the str ip and handle the local ip.
    Just 0.0.0.0 and :: will be formatted, others will be stringify and returned.
    Sorry for the bad name, haha.

    Parameters:
        host (IPv4Address | IPv6Address): The host to handle.

    Returns:
        str: The handled host.
    """
    is_v4 = host.version == 4
    if is_ip_private(host):
        return "127.0.0.1" if is_v4 else "[::1]"
    return host.compressed


def is_port_used(port: int, host: str) -> bool:
    """
    Check if the port is used.

    Parameters:
        port (int): The port to check.
        host (str): The host to check.

    Returns:
        bool: If the port is used.
    """
    try:
        socket(AF_INET, SOCK_STREAM).connect((host, port))
        return True
    except:
        return False


def is_ip_private(ip: IPv4Address | IPv6Address) -> bool:
    """
    Check if the ip is a private ip.

    Parameters:
        ip (IPv4Address | IPv6Address): The ip to check.

    Returns:
        bool: If the ip is a private ip.
    """
    return ip.is_private


def get_next_unused_port(port: int, host: str) -> int | None:
    """
    Get the next unused port from the host, starting from the port. If the port is used, it will try to find the next
    port. If the port is not used, it will return the port. If the port is out of range, it will return None.

    Parameters:
        port (int): The port to start from.
        host (str): The host to check.

    Returns:
        int | None: Port or failure.
            int: The next unused port.
            None: If the port is out of range.
    """
    now_port = port
    while is_port_used(now_port, host):
        if now_port > 65535:
            return None
        now_port += 1
    return now_port


def get_previous_unused_port(port: int, host: str) -> int | None:
    """
    Get the previous unused port from the host, starting from the port. If the port is used, it will try to find the
    previous port. If the port is not used, it will return the port. If the port is out of range, it will return None.

    Parameters:
        port (int): The port to start from.
        host (str): The host to check.

    Returns:
        int | None: Port or failure.
            int: The previous unused port.
            None: If the port is out of range.
    """
    now_port = port
    while is_port_used(now_port, host):
        if now_port < 0:
            return None
        now_port -= 1
    return now_port


def get_unused_port_from(port: int, host: IPv4Address | IPv6Address) -> int:
    """
    Get an unused port from the host, starting from the port. If the port is used, it will try to find the next or
    previous port. If the port is not used, it will return the port. If the port is out of range, it will raise an
    exception to tell you that there is no available port.

    Parameters:
        port (int): The port to start from.
        host (IPv4Address | IPv6Address): The host to check.

    Returns:
        int: The unused port.

    Raises:
        RuntimeError: If there is no available port. (Means the port is out of range.)

    Notes:
        Ah, Funix will definitely call this function when it starts up. For Funix, there is no need to catch this
        exception, just let Funix crash when all ports are used.
    """
    new_port = port
    new_host = get_compressed_ip_address_as_str(host)
    if is_port_used(new_port, new_host):
        print(f"port {port} is used, try to find next or previous port.")
        next_port = get_next_unused_port(new_port, new_host)
        if next_port is None:
            previous_port = get_previous_unused_port(new_port, new_host)
            if previous_port is None:
                raise RuntimeError(f"No available port for {new_host}, base: {port}")
            else:
                return previous_port
        else:
            return next_port
    return new_port
