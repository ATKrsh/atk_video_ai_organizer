import pytest
import hashlib
from pathlib import Path

def test_sha256_hashing(tmp_path):
    # Create a temporary file with known content
    file_path = tmp_path / "sample.txt"
    content = b"OpenAI"
    file_path.write_bytes(content)
    # Expected SHA-256
    expected = hashlib.sha256(content).hexdigest()
    # Compute using the scanner utility function
    from media.scanner import compute_sha256
    result = compute_sha256(file_path)
    assert result == expected
