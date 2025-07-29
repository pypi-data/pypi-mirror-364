"""This Module will connect to Lancom Routers in our Environment"""
from dataclasses import dataclass, field
import time
import csv
import requests
from netmiko import ConnectHandler
from subprocess import call   as system_call  # Execute a shell command
from platform   import system as system_name  # Returns the system/OS name
import subprocess
import logging
from datetime import datetime
from .credauth import cred
from .common import DefaultDict
import re

WLANDEVICES = '/etc/Credentials/WLAN_no_alarm_devices.csv'

@dataclass
class Lancom(DefaultDict):
    """Control Lancom Router

    Args:
        DefaultDict (_type_): _description_
    """
    host: str | None = None
    wlanlist: list = field(default_factory=list)
    prevlogins: int = 0
    logins: list = field(default_factory=list)
    stations: str | None = None
    status: int = 500
    status_code: int = 500
    failure: str = ""
    runtime: float = -1
    connection: None = None
    #connection: None = None

    def __post_init__(self):
        start = time.time()
        self.get_credentials()
        self.establish_connection()
        #self.check_Connection()
        end = time.time()
        self.runtime = round(end - start, 2)

    def get_credentials(self) -> bool:
        """Get Credentials for host

        Returns:
            bool: Successful or Not
        """
        try:
            self.__credentials = cred(self.host)
            return True
        except Exception as e:
            self.failure = f"get_Credentials failed with {e}"
            self.status = 500
            return False

    def establish_connection(self) -> bool:
        """Establish a Connection to host (initially)

        Returns:
            bool: True or False, if Connection was successful or not
        """        
        try:
            self.get_credentials()
            self.__credentials.update({"session_log": f"{self.host}_netmiko_session.log", 'ssh_strict': False})
            self.connection = ConnectHandler(**(self.__credentials))
            self.connection.keepalive=1
            self.connection.remote_conn.transport.set_keepalive(1)
            if self.connection.is_alive():
                self.status = 200
                return True
            else:
                return False
        except Exception as e:
            self.failure = f"We could not establish a connection to {self.host} because of {e}"
            return False

    def check_connection(self) -> bool:
        """Check if Connection to host is up or reestablish session

        Returns:
            bool: _description_
        """
        # pyfhem1
        try:
            if self.connection.is_alive() is False:
                self.get_credentials()
                self.__credentials.update({"session_log": f"{self.host}_netmiko_session.log", 'ssh_strict': False})
                self.connection = ConnectHandler(**(self.__credentials))
                self.connection.keepalive=1
                self.connection.remote_conn.transport.set_keepalive(1)
                if self.connection.is_alive() is True:
                    self.status = 200
                    return True
                else:
                    return False
        except Exception as e:
            self.get_credentials()
            self.__credentials.update({"session_log": f"{self.host}_netmiko_session.log", 'ssh_strict': False})
            self.connection = ConnectHandler(**(self.__credentials))
            self.connection.keepalive=1
            if self.connection.is_alive():
                return True
            else:
                return False

    def get_loggedin_users(self) -> str:
        """Get Loggedin Users from Router

        Returns:
            str: _description_
        """
        try:
            self.logins = []
            self.check_connection()
            self.get_wlan_devices()
            stations = self.connection.send_command('list Status/WLAN/Station-Table/')
            #logging.info(f"stations: {stations}")
            for station in stations.splitlines():
                #if (Tania.lower() in station.lower() or Papa.lower() in station.lower() or Jochen.lower() in station.lower()) and 'connected' in station.lower():
                for entry in self.wlanlist:
                    name = entry[0]
                    mac = entry[1]
                    #logging.info(f"station.lower: {station.lower()}")
                    if (mac.lower() in station.lower() and 'connected' in station.lower()):
                        eingeloggt=1
                        if mac.lower() not in self.logins:
                            self.logins.append(f'INFO: {self.host} {name} eingeloggt: {eingeloggt}')
                        #if "leer" in self.logins:
                        #    self.logins.remove("leer")
                        #if 'INFO: {} {} eingeloggt: {}'.format(self.host, name, eingeloggt) not in self.logins:
                        #    self.logins.append('INFO: {} {} eingeloggt: {}'.format(self.host, name, eingeloggt))
                        #    logging.info('INFO: {} {} eingeloggt: {}'.format(self.host, name, eingeloggt))
                    elif (mac.lower() in station.lower() and not 'connected' in station.lower()):
                        if f'INFO: {self.host} {name} eingeloggt: 1' in self.logins:
                            self.logins.remove(f'INFO: {self.host} {name} eingeloggt: 1')
                        #if 'INFO: {} {} eingeloggt: {}'.format(self.host, name, eingeloggt) in self.logins:
                        #    logging.debug("loggedin Else router {}".format(self.host))
                        #    self.logins.remove('INFO: {} {} eingeloggt: 1'.format(self.host, name))
            self.status = 200
            #return str(self.logins)
            return self.logins
        except Exception as e:
            self.status = 500
            self.failure = f"Exception in get_loggedin_users with Exception {e}"

        #return (preveingeloggt, eingeloggt, self.logins)

    def find(self, value:str = "empty") -> list:
        """_summary_

        Args:
            value (str, optional): _description_. Defaults to "empty".

        Returns:
            list: _description_
        """
        result = []
        if value != "empty":
            self.get_wlan_devices()
            self.get_loggedin_users()
            if value in self.logins:
                for line in self.logins:
                    if value in line:
                        result.append(line)
            return result


    def get_wlan_devices(self) -> None:
        """Get all WLAN Devices from File which should decide over adaptive WLAN switch off
        """
        self.wlanlist = []
        with open (WLANDEVICES, 'r', encoding="utf8") as myfile:
            wlan_dict = csv.DictReader(myfile)
            for row in wlan_dict:
                if 'ja' in row['aktiv']:
                    name, mac = row['Handyname'], row['MAC-Adresse']
                    self.wlanlist.append((name, mac))
        if len(self.wlanlist) > 0:
            self.status = 200
        else:
            self.status = 500
            self.failure = f"We could not get a list of WLAN Devices count is {len(self.wlanlist)}"

    def execute(self, value) -> str:
        try:
            self.check_connection()
            if re.match("^show ",value):
                logging.info(f"Value: {value} send to Router {self.host}")
                result = self.connection.send_command(value)
            else:
                result = "Only Show Commands are supported."
            self.status == 200
            return str(result)
        except Exception as e:
            self.status = 500
            self.failure = f"Exception in execute with Exception {e}"
