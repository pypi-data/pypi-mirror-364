from __future__ import annotations
import typing
__all__ = ['PortForwarder', 'WebServer']
class PortForwarder:
    """
    Forward ports to another host.  This is primarily useful for accessing
    Ethernet-connected devices from a computer tethered to the RoboRIO USB port.
    """
    @staticmethod
    def getInstance() -> PortForwarder:
        """
        Get an instance of the PortForwarder class.
        
        This is a singleton to guarantee that there is only a single instance
        regardless of how many times GetInstance is called.
        """
    def add(self, port: typing.SupportsInt, remoteHost: str, remotePort: typing.SupportsInt) -> None:
        """
        Forward a local TCP port to a remote host and port.
        Note that local ports less than 1024 won't work as a normal user.
        
        :param port:       local port number
        :param remoteHost: remote IP address / DNS name
        :param remotePort: remote port number
        """
    def remove(self, port: typing.SupportsInt) -> None:
        """
        Stop TCP forwarding on a port.
        
        :param port: local port number
        """
class WebServer:
    """
    A web server using the HTTP protocol.
    """
    @staticmethod
    def getInstance() -> WebServer:
        """
        Get an instance of the WebServer class.
        
        This is a singleton to guarantee that there is only a single instance
        regardless of how many times GetInstance is called.
        """
    def start(self, port: typing.SupportsInt, path: str) -> None:
        """
        Create a web server at the given port.
        Note that local ports less than 1024 won't work as a normal user. Also,
        many ports are blocked by the FRC robot radio; check the game manual for
        what is allowed through the radio firewall.
        
        :param port: local port number
        :param path: local path to document root
        """
    def stop(self, port: typing.SupportsInt) -> None:
        """
        Stop web server running at the given port.
        
        :param port: local port number
        """
