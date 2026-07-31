from XAgent.file_utils import write_binary_file


def test_write_binary_file_creates_destination_directory(tmp_path):
    destination = tmp_path / "local_workspace"

    result = write_binary_file(str(destination), "result.png", b"image")

    assert result == str(destination / "result.png")
    assert (destination / "result.png").read_bytes() == b"image"
