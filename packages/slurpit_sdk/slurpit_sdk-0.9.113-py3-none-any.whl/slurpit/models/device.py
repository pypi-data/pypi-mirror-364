from slurpit.models.basemodel import BaseModel

class Device(BaseModel):
    """
    This class represents a network device with various attributes.

    Args:
        id (int): Unique identifier for the device.
        hostname (str): Hostname of the device.
        fqdn (str): Fully qualified domain name of the device.
        device_os (str): Operating system running on the device.
        disabled (int): Indicates whether the device is disabled (0 or 1).
        os_version (str, optional): Device OS version.
        serial (str, optional): Device Hardware Serial collected by SNMP.
        snmp_contact (str, optional): Device Contact collected by SNMP.
        snmp_description (str, optional): Device Description collected by SNMP.
        snmp_location (str, optional): Device Location collected by SNMP.
        snmp_uptime (str, optional): Device Uptime collected by SNMP.
        device_type (str, optional): Type of the device, such as 'router' or 'switch'.
        brand (str, optional): Brand of the device, e.g., 'Cisco'.
        added (str, optional): Date when the device was added to the system.
        last_seen (str, optional): Last date when the device was active or seen.
        port (int, optional): Network port number primarily used by the device.
        ipv4 (str, optional): IPv4 address assigned to the device.
        vault (str, readonly): Vault username.
        vault_id (int, optional): Configured vault id.
        site (str, optional): Site Name as created in Sites. When not defined site rules will apply.
        createddate (str, optional): The date the device record was created.
        changeddate (str, optional): The date the device record was last modified.
    """
        
    def __init__(
        self,
        id: int,
        hostname: str,
        fqdn: str,
        device_os: str,
        disabled: int,
        os_version: str = None,
        serial: str = None,
        snmp_contact: str = None,
        snmp_description: str = None,
        snmp_location: str = None,
        snmp_uptime: str = None,
        telnet:int = None,
        device_type: str = None,
        brand: str = None,
        added: str = None,
        last_seen: str = None,
        port: int = None,
        ipv4: str = None,
        ipv6: str = None,
        vault: str = None,
        vault_id: int = None,
        site: str = None,
        description: str = None,
        createddate: str = None,
        changeddate: str = None,
    ):
        self.id = int(id)
        self.hostname = hostname
        self.fqdn = fqdn
        self.port = int(port)
        self.ipv4 = ipv4
        self.ipv6 = ipv6 if ipv6 is not None else None
        self.device_os = device_os
        self.telnet = int(telnet)
        self.disabled = int(disabled)
        self.os_version = os_version
        self.serial = serial
        self.snmp_contact = snmp_contact
        self.snmp_description = snmp_description
        self.snmp_location = snmp_location
        self.snmp_uptime = snmp_uptime
        self.device_type = device_type
        self.brand = brand
        self.added = added
        self.last_seen = last_seen
        self.vault = vault
        self.vault_id = vault_id
        self.site = site
        self.description = description if description is not None else None
        self.createddate = createddate
        self.changeddate = changeddate

class Vendor(BaseModel):
    """
    This class represents a vendor, defined primarily by the operating system and brand.

    Args:
        device_os (str): Operating system commonly associated with the vendor.
        brand (str): Brand name of the vendor, e.g., 'Apple' or 'Samsung'.
    """
    def __init__(
        self,
        device_os: str,
        brand: str,
        telnet: str = None
    ):
       
        self.device_os = device_os
        self.brand = brand
        self.telnet = telnet
