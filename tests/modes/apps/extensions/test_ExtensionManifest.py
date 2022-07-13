import os
import pytest
from ulauncher.api.shared.errors import ExtensionError
from ulauncher.modes.extensions.ExtensionManifest import ExtensionManifest, ExtensionManifestError


class TestExtensionManifest:

    @pytest.fixture
    def valid_manifest(self):
        return {
            "required_api_version": "1",
            "name": "Timer",
            "developer_name": "Aleksandr Gornostal",
            "icon": "images/timer.png",
            "preferences": [{
                "id": "keyword",
                "type": "keyword",
                "name": "Timer",
                "default_value": "ti"
            }]
        }

    def test_open__manifest_file__is_read(self):
        ext_dir = os.path.dirname(os.path.abspath(__file__))
        manifest = ExtensionManifest.new_from_file(f"{ext_dir}/test_extension/manifest.json")
        assert manifest.name == "Test Extension"

    def test_validate__name_empty__exception_raised(self):
        manifest = ExtensionManifest({"required_api_version": "1"})
        with pytest.raises(ExtensionManifestError) as e:
            manifest.validate()
        assert e.value.error_name == ExtensionError.InvalidManifest.value

    def test_validate__valid_manifest__no_exceptions_raised(self, valid_manifest):
        manifest = ExtensionManifest(valid_manifest)
        manifest.validate()

    def test_validate__prefs_empty_id__exception_raised(self, valid_manifest):
        valid_manifest['preferences'] = [{}]
        manifest = ExtensionManifest(valid_manifest)
        with pytest.raises(ExtensionManifestError) as e:
            manifest.validate()
        assert e.value.error_name == ExtensionError.InvalidManifest.value

    def test_validate__prefs_incorrect_type__exception_raised(self, valid_manifest):
        valid_manifest['preferences'] = [
            {'id': 'id', 'type': 'incorrect'}
        ]
        manifest = ExtensionManifest(valid_manifest)
        with pytest.raises(ExtensionManifestError) as e:
            manifest.validate()
        assert e.value.error_name == ExtensionError.InvalidManifest.value

    def test_validate__type_kw_empty_name__exception_raised(self, valid_manifest):
        valid_manifest['preferences'] = [
            {'id': 'id', 'type': 'incorrect', 'keyword': 'kw'}
        ]
        manifest = ExtensionManifest(valid_manifest)
        with pytest.raises(ExtensionManifestError) as e:
            manifest.validate()
        assert e.value.error_name == ExtensionError.InvalidManifest.value

    def test_validate__raises_error_if_empty_default_value_for_keyword(self, valid_manifest):
        valid_manifest['preferences'] = [
            {'id': 'id', 'type': 'keyword', 'name': 'My Keyword'}
        ]
        manifest = ExtensionManifest(valid_manifest)
        with pytest.raises(ExtensionManifestError) as e:
            manifest.validate()
        assert e.value.error_name == ExtensionError.InvalidManifest.value

    def test_validate__doesnt_raise_if_empty_default_value_for_non_keyword(self, valid_manifest):
        valid_manifest['preferences'] = [
            {'id': 'id', 'type': 'keyword', 'name': 'My Keyword', 'default_value': 'kw'},
            {'id': 'city', 'type': 'input', 'name': 'City'},
        ]
        manifest = ExtensionManifest(valid_manifest)
        manifest.validate()

    def test_check_compatibility__manifest_version_3__exception_raised(self):
        manifest = ExtensionManifest({"name": "Test", "required_api_version": "3"})
        with pytest.raises(ExtensionManifestError) as e:
            manifest.check_compatibility()
        assert e.value.error_name == ExtensionError.Incompatible.value

    def test_check_compatibility__manifest_version_0__exception_raised(self):
        manifest = ExtensionManifest({"name": "Test", "required_api_version": "0"})
        with pytest.raises(ExtensionManifestError) as e:
            manifest.check_compatibility()
        assert e.value.error_name == ExtensionError.Incompatible.value

    def test_check_compatibility__api_version__no_exceptions(self):
        manifest = ExtensionManifest({"name": "Test", "required_api_version": "2"})
        manifest.check_compatibility()

    def test_defaults_not_included_in_stringify(self):
        # Ensure defaults don't leak
        assert ExtensionManifest().stringify() == "{}"
        assert ExtensionManifest(preferences=[{"name": "asdf"}]).stringify() == '{"preferences": [{"name": "asdf"}]}'

    def test_get_preference(self):
        manifest = ExtensionManifest(preferences=[
            {"name": "my_text", "type": "text"},
            {"name": "my_number", "type": "number", "min": 0, "max": None}
        ])
        assert manifest.get_preference(name="my_text").type == "text"
        assert manifest.get_preference(type="number").name == "my_number"
        assert manifest.get_preference(min=0, max=None).type == "number"

    def test_get_user_preferences(self):
        manifest = ExtensionManifest(preferences=[
            {"id": "text_id", "type": "text", "value": "asdf"},
            {"id": "number_id", "type": "number", "value": 11}
        ])
        assert manifest.get_preferences_dict() == {"text_id": "asdf", "number_id": 11}
