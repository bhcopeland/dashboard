from django.test import SimpleTestCase

from kernelCI_app.management.commands.update_hardware_registry import (
    filter_entity_fields,
    unwrap_namespace,
)
from kernelCI_app.models import HardwareRegistryPlatform


class TestUnwrapNamespace(SimpleTestCase):
    def test_unwraps_namespaced_content(self):
        wrapped = {"hardware_registry": {"registries": ["ti.yaml"]}}
        self.assertEqual(unwrap_namespace(wrapped), {"registries": ["ti.yaml"]})

    def test_passes_through_unwrapped_legacy_format(self):
        legacy = {"registries": ["ti.yaml"]}
        self.assertEqual(unwrap_namespace(legacy), legacy)

    def test_does_not_unwrap_when_other_top_level_keys(self):
        data = {"hardware_registry": {}, "other": 1}
        self.assertEqual(unwrap_namespace(data), data)


class TestFilterEntityFields(SimpleTestCase):
    def test_keeps_known_fields_including_compatible(self):
        entry = {
            "id": "am62-sk",
            "type": "evaluation_board",
            "vendor_id": "ti",
            "processor_id": "am625",
            "url": "https://example.com",
            "compatible": ["ti,am625-sk", "ti,am625"],
        }
        kept, dropped = filter_entity_fields(HardwareRegistryPlatform, entry)
        self.assertEqual(dropped, [])
        self.assertEqual(kept["compatible"], ["ti,am625-sk", "ti,am625"])
        self.assertEqual(kept["vendor_id"], "ti")

    def test_drops_unknown_fields(self):
        entry = {
            "id": "am62-sk",
            "vendor_id": "ti",
            "processor_id": "am625",
            "memory_mb": 2048,
            "storage_gb": 16,
        }
        kept, dropped = filter_entity_fields(HardwareRegistryPlatform, entry)
        self.assertEqual(dropped, ["memory_mb", "storage_gb"])
        self.assertNotIn("memory_mb", kept)
        self.assertEqual(kept["id"], "am62-sk")
