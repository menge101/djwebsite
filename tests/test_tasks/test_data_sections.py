import pytest
from invoke import Context

# Assuming the code is in a file called 'section_tasks.py'
# Adjust the import based on your actual file structure
from tasks.data.section import create, remove


@pytest.fixture
def mock_context(mocker):
    """Fixture for mocked invoke Context."""
    return mocker.Mock(spec=Context)


@pytest.fixture
def table_name():
    """Fixture for default table name."""
    return "test-table"


@pytest.fixture
def section_name():
    """Fixture for default section name."""
    return "test-section"


@pytest.fixture
def mock_dynamodb_table(mocker):
    """Fixture for mocked DynamoDB table."""
    mock_table = mocker.Mock()
    mock_dynamodb = mocker.Mock()
    mock_dynamodb.Table.return_value = mock_table
    mock_boto3_resource = mocker.patch("tasks.data.section.boto3.resource", return_value=mock_dynamodb)

    return {"table": mock_table, "dynamodb": mock_dynamodb, "boto3_resource": mock_boto3_resource}


@pytest.fixture
def mock_dynamodb_client(mocker):
    """Fixture for mocked DynamoDB client."""
    mock_client = mocker.Mock()
    mock_boto3_client = mocker.patch("tasks.data.section.boto3.client", return_value=mock_client)

    return {"client": mock_client, "boto3_client": mock_boto3_client}


class TestCreateTask:
    """Test cases for the create task function."""

    def test_create_with_default_active_false(self, mock_context, table_name, section_name, mock_dynamodb_table):
        """Test create task with default active=False."""
        # Act
        result = create(mock_context, table_name, section_name)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "section", "sk": section_name, "active": False}
        )
        assert result is True

    def test_create_with_active_true(self, mock_context, table_name, section_name, mock_dynamodb_table):
        """Test create task with active=True."""
        # Arrange
        active = True

        # Act
        result = create(mock_context, table_name, section_name, active)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "section", "sk": section_name, "active": True}
        )
        assert result is True

    def test_create_with_active_false_explicit(self, mock_context, table_name, section_name, mock_dynamodb_table):
        """Test create task with explicit active=False."""
        # Arrange
        active = False

        # Act
        result = create(mock_context, table_name, section_name, active)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "section", "sk": section_name, "active": False}
        )
        assert result is True

    def test_create_with_different_table_and_section_names(self, mock_context, mock_dynamodb_table):
        """Test create task with different table and section names."""
        # Arrange
        table_name = "production-sections-table"
        section_name = "user-profile-section"
        active = True

        # Act
        result = create(mock_context, table_name, section_name, active)

        # Assert
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with(table_name)
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "section", "sk": section_name, "active": True}
        )
        assert result is True


class TestRemoveTask:
    """Test cases for the remove task function."""

    def test_remove_section(self, mock_context, table_name, section_name, mock_dynamodb_client):
        """Test remove task functionality."""
        # Act
        result = remove(mock_context, table_name, section_name)

        # Assert
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName=table_name, Key={"sk": section_name, "pk": "section"}
        )
        assert result is True

    def test_remove_with_different_table_and_section_names(self, mock_context, mock_dynamodb_client):
        """Test remove task with different table and section names."""
        # Arrange
        table_name = "production-sections-table"
        section_name = "user-profile-section"

        # Act
        result = remove(mock_context, table_name, section_name)

        # Assert
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName=table_name, Key={"sk": section_name, "pk": "section"}
        )
        assert result is True

    def test_remove_section_key_structure(self, mock_context, mock_dynamodb_client):
        """Test that remove uses correct key structure for DynamoDB."""
        # Arrange
        table_name = "test-table"
        section_name = "special-section-123"

        # Act
        result = remove(mock_context, table_name, section_name)

        # Assert
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        # Verify the key structure has both pk and sk with correct values
        expected_key = {"sk": section_name, "pk": "section"}
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(TableName=table_name, Key=expected_key)
        assert result is True


class TestCollectionSetup:
    """Test cases for the collection setup."""

    def test_collection_exists(self):
        """Test that the section collection is properly created."""
        from tasks.data import section

        assert section.name == "section"
        assert len(section.tasks) == 2
        assert "create" in section.tasks
        assert "remove" in section.tasks

    def test_tasks_are_callable(self):
        """Test that tasks in collection are callable."""
        from tasks.data import section

        create_task = section.tasks["create"]
        remove_task = section.tasks["remove"]

        assert callable(create_task)
        assert callable(remove_task)


# Integration-style tests (still using mocks but testing more of the flow)
class TestIntegration:
    """Integration-style tests for the section management tasks."""

    def test_create_full_flow(self, mock_context, mock_dynamodb_table):
        """Test the full create flow with all components."""
        # Act
        result = create(mock_context, "my-table", "my-section", True)

        # Assert
        assert result is True
        mock_dynamodb_table["boto3_resource"].assert_called_once_with("dynamodb")
        mock_dynamodb_table["dynamodb"].Table.assert_called_once_with("my-table")
        mock_dynamodb_table["table"].put_item.assert_called_once_with(
            Item={"pk": "section", "sk": "my-section", "active": True}
        )

    def test_remove_full_flow(self, mock_context, mock_dynamodb_client):
        """Test the full remove flow with all components."""
        # Act
        result = remove(mock_context, "my-table", "my-section")

        # Assert
        assert result is True
        mock_dynamodb_client["boto3_client"].assert_called_once_with("dynamodb")
        mock_dynamodb_client["client"].delete_item.assert_called_once_with(
            TableName="my-table", Key={"sk": "my-section", "pk": "section"}
        )
