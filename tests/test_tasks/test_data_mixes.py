import pytest
from invoke import Context

# Assuming the code is in a file called 'mix_tasks.py'
# Adjust the import based on your actual file structure
from tasks.data.mix import remove, upload


@pytest.fixture
def mock_context(mocker):
    """Fixture for mocked invoke Context."""
    return mocker.Mock(spec=Context)


@pytest.fixture
def table_name():
    """Fixture for default table name."""
    return "test-table"


@pytest.fixture
def mix_id():
    """Fixture for default mix ID."""
    return "test-mix-123"


@pytest.fixture
def source():
    """Fixture for default source."""
    return "s3://bucket/path/to/mix.mp3"


@pytest.fixture
def mock_dynamodb_table(mocker):
    """Fixture for mocked DynamoDB table."""
    mock_table = mocker.Mock()
    mock_dynamodb = mocker.Mock()
    mock_dynamodb.Table.return_value = mock_table
    mock_boto3_resource = mocker.patch("tasks.data.mix.boto3.resource", return_value=mock_dynamodb)

    return {"table": mock_table, "dynamodb": mock_dynamodb, "boto3_resource": mock_boto3_resource}


@pytest.fixture
def mock_dynamodb_client(mocker):
    """Fixture for mocked DynamoDB client."""
    mock_client = mocker.Mock()
    mock_boto3_client = mocker.patch("tasks.data.mix.boto3.client", return_value=mock_client)

    return {"client": mock_client, "boto3_client": mock_boto3_client}


class TestRemoveTask:
    """Test cases for the remove task function."""

    def test_remove_mix(self, mock_context, table_name, mix_id, mock_dynamodb_client):
        """Test remove task functionality."""
        # Act
        result = remove(mock_context, table_name, mix_id)

        # Assert
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName=table_name, Key={"pk": {"S": "mixes"}, "sk": {"S": mix_id}}
        )
        assert result is True

    def test_remove_with_different_table_and_mix_id(self, mock_context, mock_dynamodb_client):
        """Test remove task with different table and mix ID."""
        # Arrange
        table_name = "production-mixes-table"
        mix_id = "electronic-mix-456"

        # Act
        result = remove(mock_context, table_name, mix_id)

        # Assert
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName=table_name, Key={"pk": {"S": "mixes"}, "sk": {"S": mix_id}}
        )
        assert result is True

    def test_remove_key_structure_with_dynamodb_format(self, mock_context, mock_dynamodb_client):
        """Test that remove uses correct DynamoDB key structure with attribute types."""
        # Arrange
        table_name = "test-table"
        mix_id = "special-mix-789"

        # Act
        result = remove(mock_context, table_name, mix_id)

        # Assert
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        # Verify the key structure includes DynamoDB attribute types
        expected_key = {"pk": {"S": "mixes"}, "sk": {"S": mix_id}}
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(TableName=table_name, Key=expected_key)
        assert result is True


class TestUploadTask:
    """Test cases for the upload task function."""

    def test_upload_mix(self, mock_context, table_name, mix_id, source, mock_dynamodb_table):
        """Test upload task functionality."""
        # Act
        result = upload(mock_context, table_name, mix_id, source)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "mixes", "sk": mix_id, "source": source}
        )
        assert result is True

    def test_upload_with_different_parameters(self, mock_context, mock_dynamodb_table):
        """Test upload task with different parameters."""
        # Arrange
        table_name = "production-mixes-table"
        mix_id = "jazz-mix-456"
        source = "s3://production-bucket/jazz/mix.wav"

        # Act
        result = upload(mock_context, table_name, mix_id, source)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "mixes", "sk": mix_id, "source": source}
        )
        assert result is True

    def test_upload_item_structure(self, mock_context, mock_dynamodb_table):
        """Test that upload creates correct item structure."""
        # Arrange
        table_name = "test-table"
        mix_id = "house-mix-789"
        source = "file:///local/path/house.flac"

        # Act
        result = upload(mock_context, table_name, mix_id, source)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        # Verify the item structure
        expected_item = {"pk": "mixes", "sk": mix_id, "source": source}
        mock_dynamodb_table["table"].put_item.assert_called_once_with(Item=expected_item)
        assert result is True

    def test_upload_with_url_source(self, mock_context, table_name, mix_id, mock_dynamodb_table):
        """Test upload with URL source."""
        # Arrange
        source = "https://example.com/api/mixes/download"

        # Act
        result = upload(mock_context, table_name, mix_id, source)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "mixes", "sk": mix_id, "source": source}
        )
        assert result is True


class TestCollectionSetup:
    """Test cases for the collection setup."""

    def test_collection_exists(self):
        """Test that the mix collection is properly created."""
        from tasks.data import mix

        assert mix.name == "mix"
        assert len(mix.tasks) == 1
        assert "upload" in mix.tasks

    def test_upload_task_is_callable(self):
        """Test that upload task in collection is callable."""
        from tasks.data import mix

        upload_task = mix.tasks["upload"]
        assert callable(upload_task)

    def test_remove_task_not_in_collection(self):
        """Test that remove task is not added to the collection."""
        from tasks.data import mix

        # Note: remove task is defined but not added to the collection
        assert "remove" not in mix.tasks


# Integration-style tests (still using mocks but testing more of the flow)
class TestIntegration:
    """Integration-style tests for the mix management tasks."""

    def test_remove_full_flow(self, mock_context, mock_dynamodb_client):
        """Test the full remove flow with all components."""
        # Act
        result = remove(mock_context, "my-table", "my-mix")

        # Assert
        assert result is True
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName="my-table", Key={"pk": {"S": "mixes"}, "sk": {"S": "my-mix"}}
        )

    def test_upload_full_flow(self, mock_context, mock_dynamodb_table):
        """Test the full upload flow with all components."""
        # Act
        result = upload(mock_context, "my-table", "my-mix", "s3://my-bucket/file.mp3")

        # Assert
        assert result is True
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with("my-table")
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "mixes", "sk": "my-mix", "source": "s3://my-bucket/file.mp3"}
        )


# Cross-function tests
class TestCrossFunctionBehavior:
    """Test cases that verify behavior across both functions."""

    def test_both_functions_use_same_pk_value(
        self, mock_context, table_name, mix_id, source, mock_dynamodb_table, mock_dynamodb_client
    ):
        """Test that both functions use the same partition key value 'mixes'."""
        # Test upload uses pk="mixes"
        upload(mock_context, table_name, mix_id, source)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "mixes", "sk": mix_id, "source": source}
        )

        # Test remove uses pk="mixes" (with DynamoDB format)
        remove(mock_context, table_name, mix_id)
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName=table_name, Key={"pk": {"S": "mixes"}, "sk": {"S": mix_id}}
        )

    def test_both_functions_return_true(
        self, mock_context, table_name, mix_id, source, mock_dynamodb_table, mock_dynamodb_client
    ):
        """Test that both functions return True on successful operation."""
        upload_result = upload(mock_context, table_name, mix_id, source)
        remove_result = remove(mock_context, table_name, mix_id)

        assert upload_result is True
        assert remove_result is True
