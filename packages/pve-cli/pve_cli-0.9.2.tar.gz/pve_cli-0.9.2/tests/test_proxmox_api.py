import pytest

from pve_cli.proxmox import ProxmoxMissingPermissionError
from pve_cli.proxmox.api import Proxmox


class TestProxmoxAPI:
    def test_check_permission(self, proxmox_api: Proxmox) -> None:
        proxmox_api.check_permission('/vms/1', 'VM.Audit')

    def test_check_permission_not_found(self, proxmox_api: Proxmox) -> None:
        with pytest.raises(ProxmoxMissingPermissionError):
            proxmox_api.check_permission('/vms/1', 'VM.Nonexistent')

    def test_cluster_info(self, proxmox_api: Proxmox) -> None:
        result = proxmox_api.cluster.info()
        assert result == {'type': 'cluster', 'nodes': 3, 'name': 'example', 'version': 1, 'quorate': 1, 'id': 'cluster'}
