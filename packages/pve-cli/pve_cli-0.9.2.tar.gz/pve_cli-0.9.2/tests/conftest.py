from pathlib import Path

import pytest
import pytest_mock
import toml
from typer.testing import CliRunner

from pve_cli.proxmox.api import Proxmox


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def valid_config() -> dict:
    return {
        'defaults': {'endpoint': 'examplecluster'},
        'endpoint': {
            'examplecluster': {
                'host': 'examplehost',
                'user': 'root',
                'realm': 'foo',
                'token_name': 'test',
                'token_secret': 'PSSST!',
            }
        },
    }


@pytest.fixture
def valid_config_file(tmp_path: Path, valid_config: dict) -> Path:
    config_file_path = tmp_path / 'config.toml'
    config = valid_config
    config_file_path.write_text(toml.dumps(config))
    return config_file_path


@pytest.fixture
def invalid_config_invalid_endpoint() -> dict:
    return {
        'defaults': {'endpoint': 'invalid'},
        'endpoint': {
            'examplecluster': {
                'host': 'examplehost',
                'user': 'root',
                'realm': 'foo',
                'token_name': 'test',
                'token_secret': 'PSSST!',
            }
        },
    }


@pytest.fixture
def invalid_config_missing_keys() -> dict:
    return {
        'defaults': {'endpoint': 'examplecluster'},
        'endpoint': {
            'examplecluster': {'host': 'examplehost', 'user': 'root', 'token_name': 'test', 'token_secret': 'PSSST!'},
            'second_cluster': {'host': 'host2', 'token_name': 'test', 'token_secret': 'PSSST!'},
        },
    }


@pytest.fixture
def valid_config_no_default_endpoint() -> dict:
    return {
        'defaults': {},
        'endpoint': {
            'examplecluster': {
                'host': 'examplehost',
                'user': 'root',
                'realm': 'foo',
                'token_name': 'test',
                'token_secret': 'PSSST!',
            }
        },
    }


@pytest.fixture
def valid_config_no_default_endpoint_file(tmp_path: Path, valid_config_no_default_endpoint: dict) -> Path:
    config_file_path = tmp_path / 'config.toml'
    config = valid_config_no_default_endpoint
    config_file_path.write_text(toml.dumps(config))
    return config_file_path


@pytest.fixture(autouse=True)
def proxmox_api(mocker: pytest_mock.MockerFixture) -> Proxmox:
    host = 'testhost'
    user = 'testuser'
    realm = 'testrealm'
    token_name = 'testtoken'  # noqa: S105
    token_secret = 'secret'  # noqa: S105

    mock_api = mocker.Mock()
    mock_api.version.get.return_value = {'data': {'version': '8.4.1', 'repoid': '2a5fa54a8503f96d', 'release': '8.4'}}
    mock_api.cluster.status.get.return_value = [
        {'type': 'cluster', 'nodes': 3, 'name': 'example', 'version': 1, 'quorate': 1, 'id': 'cluster'},
        {
            'type': 'node',
            'nodeid': 1,
            'online': 1,
            'id': 'node/node-1',
            'name': 'node-1',
            'ip': '2001:db8::8006:1',
            'local': 1,
            'level': '',
        },
        {
            'type': 'node',
            'nodeid': 2,
            'online': 1,
            'id': 'node/node-2',
            'name': 'node-2',
            'ip': '2001:db8::8006:2',
            'local': 0,
            'level': '',
        },
        {
            'type': 'node',
            'nodeid': 3,
            'online': 1,
            'id': 'node/node-3',
            'name': 'node-3',
            'ip': '2001:db8::8006:3',
            'local': 0,
            'level': '',
        },
    ]
    mock_api.access.permissions.get.return_value = {
        '/vms/1': {
            'Realm.AllocateUser': 1,
            'Sys.Audit': 1,
            'Datastore.Audit': 1,
            'Datastore.Allocate': 1,
            'Mapping.Audit': 1,
            'Sys.Incoming': 1,
            'SDN.Audit': 1,
            'VM.Migrate': 1,
            'Datastore.AllocateTemplate': 1,
            'VM.Config.Disk': 1,
            'Pool.Allocate': 1,
            'Sys.Syslog': 1,
            'VM.Audit': 1,
            'SDN.Allocate': 1,
            'VM.Config.HWType': 1,
            'Datastore.AllocateSpace': 1,
            'VM.Console': 1,
            'Sys.Console': 1,
            'VM.Config.Options': 1,
            'VM.Config.CPU': 1,
            'Realm.Allocate': 1,
            'Mapping.Modify': 1,
            'Mapping.Use': 1,
            'Sys.AccessNetwork': 1,
            'VM.Monitor': 1,
            'VM.Allocate': 1,
            'VM.Config.CDROM': 1,
            'VM.Clone': 1,
            'VM.Snapshot': 1,
            'Group.Allocate': 1,
            'VM.Config.Memory': 1,
            'User.Modify': 1,
            'Permissions.Modify': 1,
            'Sys.Modify': 1,
            'SDN.Use': 1,
            'VM.Config.Network': 1,
            'Sys.PowerMgmt': 1,
            'VM.PowerMgmt': 1,
            'VM.Backup': 1,
            'VM.Config.Cloudinit': 1,
            'Pool.Audit': 1,
            'VM.Snapshot.Rollback': 1,
        },
    }

    mocker.patch('pve_cli.proxmox.api.ProxmoxAPI', return_value=mock_api)

    return Proxmox(host=host, user=user, realm=realm, token_name=token_name, token_secret=token_secret)
