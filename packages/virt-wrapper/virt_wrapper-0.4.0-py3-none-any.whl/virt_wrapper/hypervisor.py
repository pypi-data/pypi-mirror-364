from .base import Base, HypervisorType
from .storage import Storage
from .vm import VirtualMachine


class Hypervisor(Base):
    """Essential class for managing the hypervisor"""

    def __init__(self, host: str, type: HypervisorType, auth: tuple[str, str]):
        Base.__init__(self, host, type, auth)
        self.driver = self._host_driver(host=host, auth=auth)

    def virtual_machines(self) -> list[VirtualMachine]:
        """Get list of virtual machines on the hypervisor"""
        return [
            VirtualMachine(host=self.host, uuid=uuid, type=self.type, auth=self.auth)
            for uuid in self.driver.get_vms_uuid()
        ]

    def import_vm(self, source: str, storage: str, name: str) -> VirtualMachine:
        """Import a virtual machine from a source path"""
        return VirtualMachine(
            host=self.host,
            uuid=self.driver.import_vm(source=source, storage=storage, name=name),
            type=self.type,
            auth=self.auth,
        )

    def storages(self) -> list[Storage]:
        """Get information about the host storage systems"""
        return [Storage(**storage) for storage in self.driver.get_storages()]
