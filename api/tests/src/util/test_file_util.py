import os

import boto3
import pytest
from smart_open import open as smart_open

import src.util.file_util as file_util
import tests.src.db.models.factories as f


def create_file(root_path, file_path):
    full_path = os.path.join(root_path, file_path)

    if not file_util.is_s3_path(str(full_path)):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with smart_open(full_path, mode="w") as outfile:
        outfile.write("hello")

    return full_path


@pytest.mark.parametrize(
    "path,is_s3",
    [
        ("s3://bucket/folder/test.txt", True),
        ("./relative/folder/test.txt", False),
        ("http://example.com/test.txt", False),
    ],
)
def test_is_s3_path(path, is_s3):
    assert file_util.is_s3_path(path) is is_s3


@pytest.mark.parametrize(
    "path,bucket,prefix",
    [
        ("s3://my_bucket/my_key", "my_bucket", "my_key"),
        ("s3://my_bucket/path/to/directory/", "my_bucket", "path/to/directory/"),
        ("s3://my_bucket/path/to/file.txt", "my_bucket", "path/to/file.txt"),
    ],
)
def test_split_s3_url(path, bucket, prefix):
    assert file_util.split_s3_url(path) == (bucket, prefix)


@pytest.mark.parametrize(
    "path,bucket",
    [
        ("s3://bucket/folder/test.txt", "bucket"),
        ("s3://bucket_x/folder", "bucket_x"),
        ("s3://bucket-y/folder/", "bucket-y"),
        ("s3://bucketz", "bucketz"),
    ],
)
def test_get_s3_bucket(path, bucket):
    assert file_util.get_s3_bucket(path) == bucket


@pytest.mark.parametrize(
    "path,file_key",
    [
        ("s3://bucket/folder/test.txt", "folder/test.txt"),
        ("s3://bucket_x/file.csv", "file.csv"),
        ("s3://bucket-y/folder/path/to/abc.zip", "folder/path/to/abc.zip"),
        ("./folder/path", "./folder/path"),
        ("sftp://folder/filename", "filename"),
    ],
)
def test_get_s3_file_key(path, file_key):
    assert file_util.get_s3_file_key(path) == file_key


@pytest.mark.parametrize(
    "path,file_name",
    [
        ("s3://bucket/folder/test.txt", "test.txt"),
        ("s3://bucket_x/file.csv", "file.csv"),
        ("s3://bucket-y/folder/path/to/abc.zip", "abc.zip"),
        ("./folder/path", "path"),
        ("sftp://filename", "filename"),
    ],
)
def test_get_s3_file_name(path, file_name):
    assert file_util.get_file_name(path) == file_name


def test_get_file_length_bytes(tmp_path):
    test_content = "Hello, World!"
    test_file = tmp_path / "test.txt"
    test_file.write_text(test_content)

    size = file_util.get_file_length_bytes(str(test_file))

    # Verify size matches content length
    assert size == len(test_content)


def test_get_file_length_bytes_s3_with_content(mock_s3_bucket):
    """Test getting file size from S3 with actual content"""
    # Create test content
    test_content = b"Test content!"
    test_file_path = f"s3://{mock_s3_bucket}/test/file.txt"

    # Upload test content to mock S3
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=mock_s3_bucket, Key="test/file.txt", Body=test_content)

    # Get file size using our utility
    size = file_util.get_file_length_bytes(test_file_path)

    # Verify size matches content length
    assert size == len(test_content)


def test_file_exists_local_filesystem(tmp_path):
    file_path1 = tmp_path / "test.txt"
    file_path2 = tmp_path / "test2.txt"
    file_path3 = tmp_path / "test3.txt"

    with file_util.open_stream(file_path1, "w") as outfile:
        outfile.write("hello")
    with file_util.open_stream(file_path2, "w") as outfile:
        outfile.write("hello")
    with file_util.open_stream(file_path3, "w") as outfile:
        outfile.write("hello")

    assert file_util.file_exists(file_path1) is True
    assert file_util.file_exists(file_path2) is True
    assert file_util.file_exists(file_path3) is True
    assert file_util.file_exists(tmp_path / "test4.txt") is False
    assert file_util.file_exists(tmp_path / "test5.txt") is False


def test_file_exists_s3(mock_s3_bucket):
    file_path1 = f"s3://{mock_s3_bucket}/test.txt"
    file_path2 = f"s3://{mock_s3_bucket}/test2.txt"
    file_path3 = f"s3://{mock_s3_bucket}/test3.txt"

    with file_util.open_stream(file_path1, "w") as outfile:
        outfile.write("hello")
    with file_util.open_stream(file_path2, "w") as outfile:
        outfile.write("hello")
    with file_util.open_stream(file_path3, "w") as outfile:
        outfile.write("hello")

    assert file_util.file_exists(file_path1) is True
    assert file_util.file_exists(file_path2) is True
    assert file_util.file_exists(file_path3) is True
    assert file_util.file_exists(f"s3://{mock_s3_bucket}/test4.txt") is False
    assert file_util.file_exists(f"s3://{mock_s3_bucket}/test5.txt") is False


def test_copy_file_s3(mock_s3_bucket, other_mock_s3_bucket):
    file_path = f"s3://{mock_s3_bucket}/my_file.txt"

    with file_util.open_stream(file_path, "w") as outfile:
        outfile.write(f.fake.sentence(25))

    other_file_path = f"s3://{other_mock_s3_bucket}/my_new_file.txt"
    file_util.copy_file(file_path, other_file_path)

    assert file_util.file_exists(file_path) is True
    assert file_util.file_exists(other_file_path) is True

    assert file_util.read_file(file_path) == file_util.read_file(other_file_path)


def test_copy_file_local_disk(tmp_path):
    file_path = tmp_path / "my_file.txt"

    with file_util.open_stream(file_path, "w") as outfile:
        outfile.write(f.fake.sentence(25))

    other_file_path = tmp_path / "my_file2.txt"
    file_util.copy_file(file_path, other_file_path)

    assert file_util.file_exists(file_path) is True
    assert file_util.file_exists(other_file_path) is True

    assert file_util.read_file(file_path) == file_util.read_file(other_file_path)


def test_move_file_s3(mock_s3_bucket, other_mock_s3_bucket):
    file_path = f"s3://{mock_s3_bucket}/my_file_to_copy.txt"

    contents = f.fake.sentence(25)
    with file_util.open_stream(file_path, "w") as outfile:
        outfile.write(contents)

    other_file_path = f"s3://{other_mock_s3_bucket}/my_destination_file.txt"
    file_util.move_file(file_path, other_file_path)

    assert file_util.file_exists(file_path) is False
    assert file_util.file_exists(other_file_path) is True

    assert file_util.read_file(other_file_path) == contents


def test_move_file_local_disk(tmp_path):
    file_path = tmp_path / "my_file_to_move.txt"

    contents = f.fake.sentence(25)
    with file_util.open_stream(file_path, "w") as outfile:
        outfile.write(contents)

    other_file_path = tmp_path / "my_moved_file.txt"
    file_util.move_file(file_path, other_file_path)

    assert file_util.file_exists(file_path) is False
    assert file_util.file_exists(other_file_path) is True

    assert file_util.read_file(other_file_path) == contents


@pytest.mark.parametrize(
    "s3_path,cdn_url,expected",
    [
        (
            "s3://local-mock-public-bucket/path/to/file.pdf",
            "https://cdn.example.com",
            "https://cdn.example.com/path/to/file.pdf",
        ),
        (
            "s3://local-mock-public-bucket/opportunities/9/attachments/79853231/manager.webm",
            "https://cdn.example.com",
            "https://cdn.example.com/opportunities/9/attachments/79853231/manager.webm",
        ),
        # Test with subdirectory in CDN URL
        (
            "s3://local-mock-public-bucket/file.txt",
            "https://cdn.example.com/assets",
            "https://cdn.example.com/assets/file.txt",
        ),
    ],
)
def test_convert_s3_to_cdn_url(s3_path, cdn_url, expected, s3_config):
    assert file_util.convert_public_s3_to_cdn_url(s3_path, cdn_url, s3_config) == expected


def test_convert_s3_to_cdn_url_invalid_path(s3_config):
    with pytest.raises(ValueError, match="Expected s3:// path"):
        file_util.convert_public_s3_to_cdn_url(
            "http://not-s3/file.txt", "cdn.example.com", s3_config
        )
