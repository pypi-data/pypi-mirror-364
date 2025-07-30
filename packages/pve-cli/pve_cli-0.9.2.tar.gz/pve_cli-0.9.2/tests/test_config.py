import pytest

from pve_cli.util.exceptions import InvalidConfigError
from pve_cli.util.validators import config_validate


class TestConfigValidate:
    def test_config_validate(self, valid_config: dict) -> None:
        try:
            config_validate(valid_config)
        except Exception as exc:
            pytest.fail(f'validate_config raised exception {exc}')

    def test_endpoint_default_invalid(self, invalid_config_invalid_endpoint: dict) -> None:
        with pytest.raises(InvalidConfigError):
            config_validate(invalid_config_invalid_endpoint)

    def test_missing_endpoint_key(self, invalid_config_missing_keys: dict) -> None:
        with pytest.raises(InvalidConfigError) as exc:
            config_validate(invalid_config_missing_keys)

        assert 'examplecluster: realm' in str(exc.value)
        assert 'second_cluster: user, realm' in str(exc.value)
