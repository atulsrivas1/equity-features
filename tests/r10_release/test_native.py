"""Actual accepted pipeline composition, full forms only; no fake native result."""
from pathlib import Path
import runpy
import unittest


class Native(unittest.TestCase):
    def test_original_public_history_receipt_and_store_composition(self):
        runpy.run_path(str(Path(__file__).resolve().parents[2]/'examples/conformance_pipeline.py'),run_name='__main__')


if __name__=='__main__':unittest.main()
