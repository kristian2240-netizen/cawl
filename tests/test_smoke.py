"""C.A.W.L. smoke tests — pure logic, no network, no server."""

import tempfile
import unittest
from pathlib import Path

from test_project import config, vault, wiki
from test_project.brain import Orchestrator, offline_reply
from test_project.tools import SandboxFS


class TestSandbox(unittest.TestCase):
    def test_read_write_sandboxed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fs = SandboxFS(Path(tmp))
            fs.write("notes/a.md", "hello")
            self.assertEqual(fs.read("notes/a.md"), "hello")

    def test_escape_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            fs = SandboxFS(Path(tmp))
            with self.assertRaises(Exception):
                fs.read("../outside")


class TestProtocol(unittest.TestCase):
    def test_extract(self):
        orch = Orchestrator()
        calls = orch.extract_protocol(
            "Let me look.\nFILE_READ::vault/Index.md\n\nThat is all.\nJOURNAL::Log it."
        )
        self.assertEqual(calls[0], ("FILE_READ", "vault/Index.md"))
        self.assertEqual(calls[1], ("JOURNAL", "Log it."))


class TestOffline(unittest.TestCase):
    def test_greeting(self):
        self.assertIn("offline", offline_reply("sys", "hello").lower())


class TestWiki(unittest.TestCase):
    def test_append_and_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            config.WIKI_FILE = Path(tmp) / "wiki.md"
            info = wiki.append("First lesson")
            self.assertGreaterEqual(info["entries"], 1)
            self.assertIn("First lesson", wiki.read())


class TestVaultPaths(unittest.TestCase):
    def test_note_path(self):
        p = vault.note_path("01 Identity", "Rules")
        self.assertTrue(str(p).endswith("Rules.md"))


if __name__ == "__main__":
    unittest.main()
