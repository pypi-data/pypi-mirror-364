"""Tests for S3 functionality using mocking."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from baresquare_sdk.aws.s3 import S3Client


class TestS3Client:
    """Test suite for S3Client class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_bucket = "test-bucket"
        self.test_key = "test/file.txt"
        self.test_local_path = Path("/tmp/test_file.txt")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_s3_client_initialization(self, mock_boto3_client):
        """Test that S3Client initializes with boto3 client."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        s3_client = S3Client()

        # Assert
        mock_boto3_client.assert_called_once_with("s3")
        assert s3_client.client == mock_client

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_download_file_success(self, mock_boto3_client):
        """Test successful file download from S3."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.download_file.return_value = None  # Success returns None

        s3_client = S3Client()

        # Act
        result = s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert
        assert result is True
        mock_client.download_file.assert_called_once_with(self.test_bucket, self.test_key, str(self.test_local_path))

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_download_file_client_error(self, mock_boto3_client):
        """Test download file handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.download_file.side_effect = ClientError(
            error_response={"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist"}},
            operation_name="download_file",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert
        assert result is False
        mock_client.download_file.assert_called_once_with(self.test_bucket, self.test_key, str(self.test_local_path))

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_download_file_logs_error(self, mock_logger, mock_boto3_client):
        """Test that download file logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="download_file",
        )
        mock_client.download_file.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with(f"Error downloading from S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_upload_file_success(self, mock_boto3_client):
        """Test successful file upload to S3."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.upload_file.return_value = None  # Success returns None

        s3_client = S3Client()

        # Act
        result = s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert
        assert result is True
        mock_client.upload_file.assert_called_once_with(str(self.test_local_path), self.test_bucket, self.test_key)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_upload_file_client_error(self, mock_boto3_client):
        """Test upload file handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.upload_file.side_effect = ClientError(
            error_response={"Error": {"Code": "InvalidBucketName", "Message": "The specified bucket is not valid"}},
            operation_name="upload_file",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert
        assert result is False
        mock_client.upload_file.assert_called_once_with(str(self.test_local_path), self.test_bucket, self.test_key)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_upload_file_logs_error(self, mock_logger, mock_boto3_client):
        """Test that upload file logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "NoSuchBucket", "Message": "Bucket not found"}},
            operation_name="upload_file",
        )
        mock_client.upload_file.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with(f"Error uploading to S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_path_conversion_download(self, mock_boto3_client):
        """Test that Path objects are converted to strings in download_file."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act
        s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert - verify string conversion happened
        mock_client.download_file.assert_called_once_with(
            self.test_bucket,
            self.test_key,
            str(self.test_local_path),  # Should be converted to string
        )

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_path_conversion_upload(self, mock_boto3_client):
        """Test that Path objects are converted to strings in upload_file."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act
        s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert - verify string conversion happened
        mock_client.upload_file.assert_called_once_with(
            str(self.test_local_path),  # Should be converted to string
            self.test_bucket,
            self.test_key,
        )

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_multiple_operations_use_same_client(self, mock_boto3_client):
        """Test that multiple operations on same S3Client instance use the same boto3 client."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act
        s3_client.download_file(self.test_bucket, "file1.txt", Path("/tmp/file1.txt"))
        s3_client.upload_file(Path("/tmp/file2.txt"), self.test_bucket, "file2.txt")

        # Assert
        # boto3.client should only be called once during initialization
        mock_boto3_client.assert_called_once_with("s3")

        # Both operations should use the same mock client
        assert mock_client.download_file.call_count == 1
        assert mock_client.upload_file.call_count == 1


# Additional test for edge cases and error scenarios
class TestS3ClientEdgeCases:
    """Test edge cases and unusual scenarios."""

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_empty_strings_handled(self, mock_boto3_client):
        """Test that empty strings are handled without crashing."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act & Assert - should not raise exceptions
        result = s3_client.download_file("", "", Path(""))
        assert result is True  # Assuming boto3 handles empty strings

        result = s3_client.upload_file(Path(""), "", "")
        assert result is True

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_special_characters_in_paths(self, mock_boto3_client):
        """Test handling of special characters in bucket names and keys."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        special_bucket = "test-bucket-with-dashes"
        special_key = "folder/subfolder/file with spaces & symbols!.txt"
        special_path = Path("/tmp/file with spaces.txt")

        # Act
        s3_client.download_file(special_bucket, special_key, special_path)

        # Assert
        mock_client.download_file.assert_called_once_with(special_bucket, special_key, str(special_path))
