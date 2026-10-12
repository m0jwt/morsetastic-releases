import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import warnings
import zipfile


spec = importlib.util.spec_from_file_location(
    "release", Path(__file__).resolve().parents[1] / "tools" / "release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "public"
        self.root.mkdir()
        (self.root / "README.md").write_text(release.BEGIN + "\n" + release.END)
        self.notes = self.base / "notes.md"
        self.notes.write_text("# V1.2\nTest release notes\n")
        self.inputs = {}
        self.metadata = {}
        self.members = {}
        for platform in ("linux", "windows"):
            folder = self.base / platform
            folder.mkdir()
            self.inputs[platform] = folder
            data = bytearray(128)
            if platform == "linux":
                data[:6] = b"\x7fELF\x02\x01"
                struct.pack_into("<H", data, 18, 62)
                binary = "morsetastic"
            else:
                data[:2] = b"MZ"
                struct.pack_into("<I", data, 60, 64)
                data[64:68] = b"PE\0\0"
                struct.pack_into("<H", data, 68, 0x8664)
                struct.pack_into("<H", data, 88, 0x20b)
                binary = "morsetastic.exe"
            data += b"Version V1.2 build 2026-10-07-abcdef0\0"
            self.members[platform] = {binary: bytes(data),
                                      "default_words.txt": b"TEST\n",
                                      "callsigns.txt": b"M0JWT\n"}
            self.metadata[platform] = {
                "version": "V1.2", "source_commit": "abcdef0" + "1" * 33,
                "build_date": "2026-10-07", "production": True,
                "platform": platform,
                "archive": f"Morsetastic-V1.2-{platform.title()}-x86_64.zip",
                "sha256": "", "files": {},
            }
            self.write_package(platform)

    def write_package(self, platform, mode=0o100755):
        info = self.metadata[platform]
        folder = self.inputs[platform]
        archive = folder / info["archive"]
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in self.members[platform].items():
                item = zipfile.ZipInfo(name)
                item.external_attr = mode << 16
                z.writestr(item, data)
        info["sha256"] = release.digest(archive.read_bytes())
        info["files"] = {name: release.digest(data)
                         for name, data in self.members[platform].items()}
        self.write_metadata(platform)

    def write_metadata(self, platform):
        (self.inputs[platform] / "BUILD_INFO.json").write_text(
            json.dumps(self.metadata[platform]))

    def prepare(self):
        return release.prepare(self.root, self.inputs["linux"], self.inputs["windows"], self.notes)

    def assert_rejected(self):
        with self.assertRaises((ValueError, KeyError)):
            self.prepare()
        self.assertFalse((self.root / "releases" / "v1.2").exists())

    def test_prepare_and_verify(self):
        self.assertEqual(self.prepare(), "v1.2")
        release.verify(self.root, "v1.2")
        self.assertIn("Latest: **V1.2**", (self.root / "README.md").read_text())

    def add_extras(self):
        for platform in ("linux", "windows"):
            self.members[platform].update({
                "extras/default_words.txt": self.members[platform]["default_words.txt"],
                "extras/callsigns.txt": self.members[platform]["callsigns.txt"],
                "extras/words400.txt": b"the\nbe\n",
                "extras/wyrazy100.txt": b"i\nw\n",
                "extras/wyrazy400.txt": b"i\nw\ndzien\n",
                "extras/README.md": b"Extra practice lists\n",
            })
            self.write_package(platform)

    def add_flat_words(self):
        for platform in ("linux", "windows"):
            self.members[platform].update({
                "words400.txt": b"the\nbe\n",
                "wyrazy100.txt": b"i\nw\n",
                "wyrazy400.txt": b"i\nw\ndzien\n",
            })
            self.write_package(platform)

    def test_prepare_flat_practice_files(self):
        self.add_flat_words()
        self.assertEqual(self.prepare(), "v1.2")
        manifest = release.verify(self.root, "v1.2")
        for info in manifest["packages"].values():
            self.assertEqual(len(info["files"]), 6)
            self.assertTrue(all("/" not in name for name in info["files"]))

    def test_different_flat_practice_files(self):
        self.add_flat_words()
        self.members["windows"]["wyrazy400.txt"] += b"inne\n"
        self.write_package("windows")
        self.assert_rejected()

    def add_languages(self):
        catalog = json.dumps({"format": 1, "code": "pl", "name": "Polski",
                              "messages": {"Letters": "Litery"}}).encode()
        for platform in ("linux", "windows"):
            self.members[platform]["languages/pl.json"] = catalog
            self.write_package(platform)

    def test_language_catalogs(self):
        self.add_flat_words()
        self.add_languages()
        self.assertEqual(self.prepare(), "v1.2")
        manifest = release.verify(self.root, "v1.2")
        self.assertIn("languages/pl.json", manifest["packages"]["linux"]["files"])

    def test_different_language_catalogs(self):
        self.add_languages()
        self.members["windows"]["languages/pl.json"] += b" "
        self.write_package("windows")
        self.assert_rejected()

    def test_bad_language_payload(self):
        for payload in (b"MZ not JSON", b"{}", b"[1]", b"null", b"\xff",
                        b" " * (128 * 1024 + 1)):
            with self.subTest(payload=payload[:20]):
                self.members["windows"]["languages/pl.json"] = payload
                self.write_package("windows")
                self.assert_rejected()

    def test_unsafe_language_names(self):
        for name in ("languages/unwanted.dll", "languages/unwanted.exe",
                     "languages/template.json", "languages/en.json",
                     "languages/../pl.json", "languages/nested/pl.json",
                     "languages/PL.json", "languages/pl.json.exe"):
            with self.subTest(name=name):
                self.members["windows"][name] = b"unwanted"
                self.write_package("windows")
                self.assert_rejected()
                del self.members["windows"][name]

    def test_unsafe_flat_names(self):
        self.add_flat_words()
        for name in ("unwanted.dll", "unwanted.exe", "README.md", "../outside.txt",
                     "nested/words.txt", ".hidden.txt", "words/", "nested\\words.txt"):
            with self.subTest(name=name):
                self.members["windows"][name] = b"unwanted"
                self.write_package("windows")
                self.assert_rejected()
                del self.members["windows"][name]

    def test_case_variant_duplicate_rejected(self):
        self.add_flat_words()
        self.members["windows"]["DEFAULT_WORDS.txt"] = self.members["windows"]["default_words.txt"]
        self.write_package("windows")
        self.assert_rejected()

    def test_mixed_flat_and_nested_layout_rejected(self):
        self.add_extras()
        self.members["linux"]["words400.txt"] = b"the\nbe\n"
        self.write_package("linux")
        self.assert_rejected()

    def test_missing_flat_files_on_one_platform(self):
        self.add_flat_words()
        del self.members["windows"]["words400.txt"]
        self.write_package("windows")
        self.assert_rejected()

    def test_prepare_with_extras(self):
        self.add_extras()
        self.assertEqual(self.prepare(), "v1.2")
        release.verify(self.root, "v1.2")

    def test_missing_extra_copy(self):
        self.add_extras()
        del self.members["linux"]["extras/callsigns.txt"]
        self.write_package("linux")
        self.assert_rejected()

    def test_stale_extra_copy(self):
        self.add_extras()
        self.members["windows"]["extras/default_words.txt"] = b"STALE\n"
        self.write_package("windows")
        self.assert_rejected()

    def test_different_extra_words(self):
        self.add_extras()
        self.members["windows"]["extras/wyrazy400.txt"] += b"inne\n"
        self.write_package("windows")
        self.assert_rejected()

    def test_different_extra_documentation(self):
        self.add_extras()
        self.members["windows"]["extras/README.md"] = b"different\n"
        self.write_package("windows")
        self.assert_rejected()

    def test_extras_missing_on_one_platform(self):
        self.add_extras()
        for name in list(self.members["windows"]):
            if name.startswith("extras/"):
                del self.members["windows"][name]
        self.write_package("windows")
        self.assert_rejected()

    def test_unsafe_extra_names(self):
        self.add_extras()
        for name in ("extras/unwanted.dll", "extras/unwanted.exe", "extras/../outside.txt",
                     "extras/nested/words.txt", "extras/.hidden.txt", "extras/", "extras\\words.txt"):
            with self.subTest(name=name):
                self.members["windows"][name] = b"unwanted"
                self.write_package("windows")
                self.assert_rejected()
                del self.members["windows"][name]

    def test_duplicate_zip_member(self):
        self.add_extras()
        info = self.metadata["linux"]
        archive = self.inputs["linux"] / info["archive"]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(archive, "a") as z:
                z.writestr("extras/words400.txt", b"the\nbe\n")
        info["sha256"] = release.digest(archive.read_bytes())
        self.write_metadata("linux")
        self.assert_rejected()

    def test_unmanifested_extra_member(self):
        self.add_extras()
        del self.metadata["linux"]["files"]["extras/words400.txt"]
        self.write_metadata("linux")
        self.assert_rejected()

    def test_extra_symlink(self):
        self.add_extras()
        info = self.metadata["linux"]
        archive = self.inputs["linux"] / info["archive"]
        with zipfile.ZipFile(archive, "w") as z:
            for name, data in self.members["linux"].items():
                item = zipfile.ZipInfo(name)
                item.external_attr = (0o120777 if name == "extras/words400.txt" else 0o100755) << 16
                z.writestr(item, data)
        info["sha256"] = release.digest(archive.read_bytes())
        self.write_metadata("linux")
        self.assert_rejected()

    def test_cannot_overwrite_release(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.prepare()

    def test_mixed_commits(self):
        self.metadata["windows"]["source_commit"] = "abcdef0" + "2" * 33
        self.write_metadata("windows")
        self.assert_rejected()

    def test_mixed_versions(self):
        self.metadata["windows"]["version"] = "V1.2.1"
        self.write_metadata("windows")
        self.assert_rejected()

    def test_changed_archive(self):
        info = self.metadata["linux"]
        (self.inputs["linux"] / info["archive"]).write_bytes(b"damaged ZIP")
        self.assert_rejected()

    def test_unexpected_member(self):
        self.members["windows"]["unwanted.dll"] = b"unexpected"
        self.write_package("windows")
        self.assert_rejected()

    def test_different_practice_files(self):
        self.members["windows"]["callsigns.txt"] = b"DIFFERENT\n"
        self.write_package("windows")
        self.assert_rejected()

    def test_wrong_binary_stamp(self):
        self.members["windows"]["morsetastic.exe"] = self.members["windows"]["morsetastic.exe"].replace(
            b"abcdef0", b"fffffff")
        self.write_package("windows")
        self.assert_rejected()

    def test_wrong_architecture(self):
        data = bytearray(self.members["windows"]["morsetastic.exe"])
        struct.pack_into("<H", data, 68, 0x14c)
        self.members["windows"]["morsetastic.exe"] = bytes(data)
        self.write_package("windows")
        self.assert_rejected()

    def test_linux_permission_missing(self):
        self.write_package("linux", mode=0o100644)
        self.assert_rejected()

    def test_symlinks_rejected(self):
        self.write_package("linux", mode=0o120777)
        self.assert_rejected()

    def test_nonproduction(self):
        self.metadata["linux"]["production"] = False
        self.write_metadata("linux")
        self.assert_rejected()

    def test_unexpected_provenance_field(self):
        self.metadata["linux"]["private_path"] = "do not publish"
        self.write_metadata("linux")
        self.assert_rejected()

    def test_extra_archive_cannot_be_published(self):
        self.prepare()
        (self.root / "releases/v1.2/linux/extra.zip").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "Unexpected files"):
            release.verify(self.root, "v1.2")

    def test_checksum_list_cannot_be_changed(self):
        self.prepare()
        (self.root / "releases/v1.2/SHA256SUMS.txt").write_text("wrong\n")
        with self.assertRaisesRegex(ValueError, "checksum list"):
            release.verify(self.root, "v1.2")

    def test_unsafe_tag(self):
        with self.assertRaises(ValueError):
            release.verify(self.root, "v../../private")

    def test_empty_notes(self):
        self.notes.write_text("")
        self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
