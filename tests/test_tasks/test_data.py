import pytest
from invoke import Context
from unittest.mock import mock_open

# Assuming the code is in ./tasks/data/__init__.py
from tasks.data import load_ddb_table


@pytest.fixture
def mock_context(mocker):
    """Fixture for mocked invoke Context."""
    return mocker.Mock(spec=Context)


@pytest.fixture
def table_name():
    """Fixture for default table name."""
    return "test-table"


@pytest.fixture
def source_file_path():
    """Fixture for default source file path."""
    return "test_data.csv"


@pytest.fixture
def sample_csv_content():
    """Fixture for sample CSV content."""
    return """id,name,status
1,Item One,active
2,Item Two,inactive
3,Item Three,active"""


@pytest.fixture
def sample_csv_rows():
    """Fixture for expected CSV rows as dictionaries."""
    return [
        {"id": "1", "name": "Item One", "status": "active"},
        {"id": "2", "name": "Item Two", "status": "inactive"},
        {"id": "3", "name": "Item Three", "status": "active"},
    ]


@pytest.fixture
def empty_csv_content():
    """Fixture for empty CSV content (headers only)."""
    return "id,name,status"


@pytest.fixture
def single_row_csv_content():
    """Fixture for CSV with single data row."""
    return """pk,sk,data
section,test-section,some data"""


@pytest.fixture
def single_row_csv_rows():
    """Fixture for expected single row CSV data."""
    return [{"pk": "section", "sk": "test-section", "data": "some data"}]


@pytest.fixture
def mock_dynamodb_table(mocker):
    """Fixture for mocked DynamoDB table."""
    mock_table = mocker.Mock()
    mock_dynamodb = mocker.Mock()
    mock_dynamodb.Table.return_value = mock_table
    mock_boto3_resource = mocker.patch("tasks.data.boto3.resource", return_value=mock_dynamodb)

    return {"table": mock_table, "dynamodb": mock_dynamodb, "boto3_resource": mock_boto3_resource}


class TestLoadDdbTable:
    """Test cases for the load_ddb_table function."""

    def test_load_multiple_rows(
        self,
        mock_context,
        table_name,
        source_file_path,
        sample_csv_content,
        sample_csv_rows,
        mock_dynamodb_table,
        mocker,
    ):
        """Test loading multiple rows from CSV to DynamoDB."""
        # Arrange
        mock_file = mock_open(read_data=sample_csv_content)
        mocker.patch("builtins.open", mock_file)

        # Act
        result = load_ddb_table(mock_context, table_name, source_file_path)

        # Assert
        assert result is True
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)

        # Verify file was opened correctly
        mock_file.assert_called_once_with(source_file_path)

        # Verify each row was put into DynamoDB
        assert mock_dynamodb_table["table"].put_item.call_count == 3
        for i, expected_row in enumerate(sample_csv_rows):
            mock_dynamodb_table["table"].put_item.assert_any_call(Item=expected_row)

    def test_load_single_row(
        self,
        mock_context,
        table_name,
        source_file_path,
        single_row_csv_content,
        single_row_csv_rows,
        mock_dynamodb_table,
        mocker,
    ):
        """Test loading single row from CSV to DynamoDB."""
        # Arrange
        mock_file = mock_open(read_data=single_row_csv_content)
        mocker.patch("builtins.open", mock_file)

        # Act
        result = load_ddb_table(mock_context, table_name, source_file_path)

        # Assert
        assert result is True
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)

        # Verify file was opened correctly
        mock_file.assert_called_once_with(source_file_path)

        # Verify the single row was put into DynamoDB
        mock_dynamodb_table["table"].put_item.assert_called_once_with(Item=single_row_csv_rows[0])

    def test_load_empty_csv(
        self, mock_context, table_name, source_file_path, empty_csv_content, mock_dynamodb_table, mocker
    ):
        """Test loading empty CSV (headers only) to DynamoDB."""
        # Arrange
        mock_file = mock_open(read_data=empty_csv_content)
        mocker.patch("builtins.open", mock_file)

        # Act
        result = load_ddb_table(mock_context, table_name, source_file_path)

        # Assert
        assert result is True
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)

        # Verify file was opened correctly
        mock_file.assert_called_once_with(source_file_path)

        # Verify no items were put into DynamoDB
        mock_dynamodb_table["table"].put_item.assert_not_called()

    def test_load_with_different_file_path(
        self, mock_context, table_name, sample_csv_content, sample_csv_rows, mock_dynamodb_table, mocker
    ):
        """Test loading with different file path."""
        # Arrange
        different_file_path = "/path/to/production_data.csv"
        mock_file = mock_open(read_data=sample_csv_content)
        mocker.patch("builtins.open", mock_file)

        # Act
        result = load_ddb_table(mock_context, table_name, different_file_path)

        # Assert
        assert result is True
        mock_file.assert_called_once_with(different_file_path)
        assert mock_dynamodb_table["table"].put_item.call_count == 3

    def test_load_with_different_table_name(
        self, mock_context, source_file_path, sample_csv_content, sample_csv_rows, mock_dynamodb_table, mocker
    ):
        """Test loading with different table name."""
        # Arrange
        different_table_name = "production-data-table"
        mock_file = mock_open(read_data=sample_csv_content)
        mocker.patch("builtins.open", mock_file)

        # Act
        result = load_ddb_table(mock_context, different_table_name, source_file_path)

        # Assert
        assert result is True
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(different_table_name)
        assert mock_dynamodb_table["table"].put_item.call_count == 3

    def test_csv_reader_processes_headers_correctly(
        self, mock_context, table_name, source_file_path, mock_dynamodb_table, mocker
    ):
        """Test that CSV reader correctly processes headers and creates dictionaries."""
        # Arrange
        csv_with_special_headers = """user_id,full_name,email_address
123,John Doe,john@example.com
456,Jane Smith,jane@example.com"""

        expected_rows = [
            {"user_id": "123", "full_name": "John Doe", "email_address": "john@example.com"},
            {"user_id": "456", "full_name": "Jane Smith", "email_address": "jane@example.com"},
        ]

        mock_file = mock_open(read_data=csv_with_special_headers)
        mocker.patch("builtins.open", mock_file)

        # Act
        result = load_ddb_table(mock_context, table_name, source_file_path)

        # Assert
        assert result is True
        assert mock_dynamodb_table["table"].put_item.call_count == 2
        for expected_row in expected_rows:
            mock_dynamodb_table["table"].put_item.assert_any_call(Item=expected_row)
