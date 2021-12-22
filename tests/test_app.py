# tests/test_edge.py

import pytest


from edge import Edge


def test_edge_init(root_directory):
    """Test __init__"""
    assert Edge(edge_path=root_directory)

