import json
import pytest
import responses
import requests
from unittest.mock import patch

from mb_pipedrive_integration.services import PipedriveService
from mb_pipedrive_integration.dataclasses import (
    PipedriveConfig,
    PersonData,
    DealData,
    OrganizationData,
)
from mb_pipedrive_integration.exceptions import (
    PipedriveAPIError,
    PipedriveNetworkError,
    PipedriveConfigError,
)


class TestPipedriveService:
    """Test individual PipedriveService methods"""

    def test_service_initialization_with_config(self):
        """Test service initialization with provided config"""
        config = PipedriveConfig(domain="test", api_token="token")
        service = PipedriveService(config)

        assert service.config == config
        assert service.base_url == "https://test.pipedrive.com/v1"

    @patch("mb_pipedrive_integration.services.PipedriveConfig.from_django_settings")
    def test_service_initialization_django_fallback(self, mock_django_config):
        """Test service initialization falling back to Django settings"""
        mock_config = PipedriveConfig(domain="django", api_token="django-token")
        mock_django_config.return_value = mock_config

        service = PipedriveService()

        assert service.config == mock_config
        mock_django_config.assert_called_once()

    @patch("mb_pipedrive_integration.services.PipedriveConfig.from_django_settings")
    @patch("mb_pipedrive_integration.services.PipedriveConfig.from_env")
    def test_service_initialization_env_fallback(self, mock_env_config, mock_django_config):
        """Test service initialization falling back to environment"""
        mock_django_config.side_effect = PipedriveConfigError("Django not available")
        mock_config = PipedriveConfig(domain="env", api_token="env-token")
        mock_env_config.return_value = mock_config

        service = PipedriveService()

        assert service.config == mock_config
        mock_django_config.assert_called_once()
        mock_env_config.assert_called_once()

    @responses.activate
    def test_make_request_get_success(self, mock_service):
        """Test successful GET request"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/test",
            json={"success": True, "data": {"test": "value"}},
            status=200,
        )

        result = mock_service._make_request("GET", "test")

        assert result is not None
        assert result["success"] is True
        assert result["data"]["test"] == "value"

    @responses.activate
    def test_make_request_post_success(self, mock_service):
        """Test successful POST request"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/test",
            json={"success": True, "data": {"id": 123}},
            status=200,
        )

        test_data = {"name": "Test"}
        result = mock_service._make_request("POST", "test", test_data)

        assert result is not None
        assert result["data"]["id"] == 123

    @responses.activate
    def test_make_request_api_failure(self, mock_service):
        """Test API request with success=false"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/test",
            json={"success": False, "error": "API Error"},
            status=200,
        )

        result = mock_service._make_request("GET", "test")
        assert result is None

    @responses.activate
    def test_make_request_http_error(self, mock_service):
        """Test API request with HTTP error status"""
        responses.add(
            responses.GET, f"{mock_service.base_url}/test", json={"error": "Not found"}, status=404
        )

        # The enhanced service should raise an exception for HTTP errors
        with pytest.raises(PipedriveAPIError) as exc_info:
            mock_service._make_request("GET", "test")

        assert exc_info.value.status_code == 404
        assert "HTTP 404" in str(exc_info.value)

    @responses.activate
    def test_create_person_minimal(self, mock_service):
        """Test creating person with minimal data"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/persons",
            json={"success": True, "data": {"id": 123, "name": "Test Person"}},
            status=200,
        )

        result = mock_service.create_person("Test Person")

        assert result is not None
        assert result["id"] == 123

        # Verify request data
        request_body = responses.calls[0].request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")
        request_data = json.loads(request_body)

        assert request_data["name"] == "Test Person"
        assert "email" not in request_data

    @responses.activate
    def test_create_person_with_all_data(self, mock_service):
        """Test creating person with all data"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/persons",
            json={"success": True, "data": {"id": 124}},
            status=200,
        )

        result = mock_service.create_person(
            name="Full Person",
            email="full@example.com",
            phone="123-456-7890",
            tags=["Tag1", "Tag2"],
        )

        assert result is not None

        # Verify request data includes all fields
        request_body = responses.calls[0].request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")
        request_data = json.loads(request_body)

        assert request_data["name"] == "Full Person"
        assert request_data["email"] == "full@example.com"
        assert request_data["phone"] == "123-456-7890"
        assert "Tag1" in request_data["label"]  # Custom tags
        assert "Tag2" in request_data["label"]

    @responses.activate
    def test_find_person_by_email_found(self, mock_service):
        """Test finding person by email when found"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/persons/search",
            json={
                "success": True,
                "data": {
                    "items": [
                        {
                            "item": {
                                "id": 123,
                                "name": "Found Person",
                                "emails": [{"value": "found@example.com"}],
                            }
                        }
                    ]
                },
            },
            status=200,
        )

        result = mock_service.find_person_by_email("found@example.com")

        assert result is not None
        assert result["id"] == 123
        assert result["name"] == "Found Person"

    @responses.activate
    def test_find_person_by_email_not_found(self, mock_service):
        """Test finding person by email when not found"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/persons/search",
            json={"success": True, "data": {"items": []}},
            status=200,
        )

        result = mock_service.find_person_by_email("notfound@example.com")
        assert result is None

    @responses.activate
    def test_create_organization(self, mock_service):
        """Test organization creation"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": {
                    "id": 456,
                    "name": "Test Org",
                }
            },
            status=200,
        )

        org_data = OrganizationData(name="Test Org")
        result = mock_service.create_organization(org_data)

        assert result is not None
        assert result["id"] == 456
        assert result["name"] == "Test Org"

    @responses.activate
    def test_find_organization_by_name(self, mock_service):
        """Test finding organization by name"""
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations/search",
            json={"success": True, "data": {"items": [{"item": {"id": 456, "name": "Found Org"}}]}},
            status=200,
        )

        result = mock_service.find_organization_by_name("Found Org")

        assert result is not None
        assert result["id"] == 456
        assert result["name"] == "Found Org"

    @responses.activate
    def test_update_deal_stage(self, mock_service):
        """Test updating deal stage"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": True, "data": {"id": 123, "stage_id": 5}},
            status=200,
        )

        result = mock_service.update_deal_stage(123, "5")
        assert result is True

    @responses.activate
    def test_update_deal_stage_failure(self, mock_service):
        """Test updating deal stage failure"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": False, "error": "Deal not found"},
            status=404,
        )

        result = mock_service.update_deal_stage(123, "5")
        assert result is False

    @responses.activate
    def test_close_deal_won(self, mock_service):
        """Test closing deal as won"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": True, "data": {"id": 123, "status": "won"}},
            status=200,
        )

        result = mock_service.close_deal(123, "won")
        assert result is True

    @responses.activate
    def test_close_deal_lost(self, mock_service):
        """Test closing deal as lost"""
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/123",
            json={"success": True, "data": {"id": 123, "status": "lost"}},
            status=200,
        )

        result = mock_service.close_deal(123, "lost")
        assert result is True

    @responses.activate
    def test_add_deal_notes(self, mock_service):
        """Test adding notes to a deal"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/notes",
            json={"success": True, "data": {"id": 999}},
            status=200,
        )

        deal_data = DealData(
            title="Test Deal",
            folder_number=12345,
            folder_id="abc-123",
            tenant=PersonData(name="John Tenant", email="tenant@example.com"),
            property_address="123 Test Street",
        )

        result = mock_service._add_deal_notes(123, deal_data)
        assert result is True

        # Verify note content includes relevant information
        request_body = responses.calls[0].request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode("utf-8")
        request_data = json.loads(request_body)

        assert request_data["deal_id"] == 123
        assert "Folder Number: 12345" in request_data["content"]
        assert "Tenant: John Tenant" in request_data["content"]
        assert "Property Address: 123 Test Street" in request_data["content"]

    def test_network_error_handling(self, mock_service):
        """Test handling of network errors"""
        # Mock requests.get to raise ConnectionError
        with patch(
            "requests.get", side_effect=requests.exceptions.ConnectionError("Network unreachable")
        ):
            with pytest.raises(PipedriveNetworkError) as exc_info:
                mock_service._make_request("GET", "test")

            assert "Network unreachable" in str(exc_info.value)
            assert exc_info.value.retry_count == 3  # max_retries

    def test_timeout_handling(self, mock_service):
        """Test handling of request timeouts"""
        # Mock requests.get to raise Timeout
        with patch("requests.get", side_effect=requests.exceptions.Timeout("Request timeout")):
            with pytest.raises(PipedriveNetworkError) as exc_info:
                mock_service._make_request("GET", "test")

            assert "timeout" in str(exc_info.value).lower()
            assert exc_info.value.retry_count == 3  # max_retries

    @responses.activate
    def test_add_deal_tags_success(self, mock_service):
        """Test adding tags to a deal successfully"""
        deal_id = 123
        tags = ["INQUILINO", "ASESOR INMOBILIARIO"]

        # Mock getting current deal (no existing tags)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": None  # No existing tags
                }
            },
            status=200
        )

        # Mock updating deal with tags
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,ASESOR INMOBILIARIO"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, tags)

        assert result is True
        assert len(responses.calls) == 2  # GET + PUT

        # Verify the PUT request data
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        actual_tags = set(request_data["label"].split(","))
        expected_tags = {"INQUILINO", "ASESOR INMOBILIARIO"}
        assert actual_tags == expected_tags


    @responses.activate
    def test_add_deal_tags_with_existing_tags(self, mock_service):
        """Test adding tags to a deal that already has tags"""
        deal_id = 123
        new_tags = ["PROPIETARIO"]

        # Mock getting current deal (with existing tags)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG"
                }
            },
            status=200
        )

        # Mock updating deal with combined tags
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG,PROPIETARIO"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, new_tags)

        assert result is True

        # Verify the PUT request includes both existing and new tags
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        # Should contain all tags (order might vary due to set operation)
        label_tags = set(request_data["label"].split(","))
        expected_tags = {"INQUILINO", "EXISTING_TAG", "PROPIETARIO"}
        assert label_tags == expected_tags


    @responses.activate
    def test_add_deal_tags_duplicate_prevention(self, mock_service):
        """Test that duplicate tags are not added"""
        deal_id = 123
        duplicate_tags = ["INQUILINO", "EXISTING_TAG"]  # INQUILINO already exists

        # Mock getting current deal (with existing tags)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG"
                }
            },
            status=200
        )

        # Mock updating deal (should be the same tags)
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "INQUILINO,EXISTING_TAG"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, duplicate_tags)

        assert result is True

        # Verify no duplicate tags in the request
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        label_tags = request_data["label"].split(",")
        # Should have only 2 unique tags, not 4
        assert len(set(label_tags)) == 2


    @responses.activate
    def test_add_deal_tags_empty_list(self, mock_service):
        """Test adding empty tag list"""
        deal_id = 123
        empty_tags = []

        result = mock_service.add_deal_tags(deal_id, empty_tags)

        assert result is True
        assert len(responses.calls) == 0  # No API calls should be made


    @responses.activate
    def test_add_deal_tags_get_deal_failure(self, mock_service):
        """Test failure when getting current deal info"""
        deal_id = 123
        tags = ["INQUILINO"]

        # Mock failed GET request
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={"success": False, "error": "Deal not found"},
            status=404
        )

        result = mock_service.add_deal_tags(deal_id, tags)

        assert result is False
        assert len(responses.calls) == 1  # Only GET call, no PUT


    @responses.activate
    def test_add_deal_tags_update_failure(self, mock_service):
        """Test failure when updating deal with tags"""
        deal_id = 123
        tags = ["INQUILINO"]

        # Mock successful GET
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": None
                }
            },
            status=200
        )

        # Mock failed PUT
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={"success": False, "error": "Update failed"},
            status=400
        )

        result = mock_service.add_deal_tags(deal_id, tags)

        assert result is False
        assert len(responses.calls) == 2  # GET + PUT


    @responses.activate
    def test_add_deal_tags_with_string_labels(self, mock_service):
        """Test handling existing labels as string (comma-separated)"""
        deal_id = 123
        new_tags = ["NEW_TAG"]

        # Mock getting current deal with string labels
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "TAG1,TAG2, TAG3 "  # Note spaces and formatting
                }
            },
            status=200
        )

        # Mock updating deal
        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/deals/{deal_id}",
            json={
                "success": True,
                "data": {
                    "id": deal_id,
                    "title": "Test Deal",
                    "label": "TAG1,TAG2,TAG3,NEW_TAG"
                }
            },
            status=200
        )

        result = mock_service.add_deal_tags(deal_id, new_tags)

        assert result is True

        # Verify the request properly handles the string parsing
        put_request = responses.calls[1].request
        import json
        request_data = json.loads(put_request.body.decode('utf-8'))

        label_tags = set(request_data["label"].split(","))
        expected_tags = {"TAG1", "TAG2", "TAG3", "NEW_TAG"}
        assert label_tags == expected_tags

    @responses.activate
    def test_find_organization_by_custom_field_found(self, mock_service):
        """Test finding organization by custom field when it exists"""
        # Set up mock config with custom fields
        mock_service.config.custom_fields = {
            "org_mb_id": "hash123",
            "org_external_id": "hash456"
        }

        # Mock API response with organizations
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": [
                    {
                        "id": 100,
                        "name": "First Org",
                        "hash123": "mb-uuid-123",  # mb_id field
                        "hash456": "ext-456"  # external_id field
                    },
                    {
                        "id": 200,
                        "name": "Second Org",
                        "hash123": "mb-uuid-789",
                        "hash456": "ext-789"
                    }
                ],
                "additional_data": {
                    "pagination": {"more_items_in_collection": False}
                }
            },
            status=200
        )

        # Test finding by mb_id
        result = mock_service.find_organization_by_custom_field("mb_id", "mb-uuid-123")

        assert result is not None
        assert result["id"] == 100
        assert result["name"] == "First Org"
        assert result["hash123"] == "mb-uuid-123"

    @responses.activate
    def test_find_organization_by_custom_field_not_found(self, mock_service):
        """Test finding organization by custom field when it doesn't exist"""
        mock_service.config.custom_fields = {"org_mb_id": "hash123"}

        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": [
                    {"id": 100, "name": "Org", "hash123": "different-value"}
                ],
                "additional_data": {
                    "pagination": {"more_items_in_collection": False}
                }
            },
            status=200
        )

        result = mock_service.find_organization_by_custom_field("mb_id", "not-found-value")
        assert result is None

    @responses.activate
    def test_find_organization_by_custom_field_pagination(self, mock_service):
        """Test finding organization with pagination"""
        mock_service.config.custom_fields = {"org_mb_id": "hash123"}

        # First page - FIXED: Include api_token in the URL pattern
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",  # Use base URL without query params
            json={
                "success": True,
                "data": [{"id": 100, "name": "Org1", "hash123": "wrong-value"}],
                "additional_data": {
                    "pagination": {"more_items_in_collection": True}
                }
            },
            status=200
        )

        # Second page (contains our target) - FIXED: Use same pattern
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",  # Use base URL without query params
            json={
                "success": True,
                "data": [{"id": 200, "name": "Target Org", "hash123": "target-value"}],
                "additional_data": {
                    "pagination": {"more_items_in_collection": False}
                }
            },
            status=200
        )

        result = mock_service.find_organization_by_custom_field("mb_id", "target-value")

        assert result is not None
        assert result["id"] == 200
        assert result["name"] == "Target Org"
        assert len(responses.calls) == 2  # Should have made 2 API calls

    def test_find_organization_by_custom_field_no_config(self, mock_service):
        """Test finding organization when no custom fields configured"""
        mock_service.config.custom_fields = None

        result = mock_service.find_organization_by_custom_field("mb_id", "test")
        assert result is None

    def test_find_organization_by_custom_field_no_mapping(self, mock_service):
        """Test finding organization when field not mapped"""
        mock_service.config.custom_fields = {"org_other_field": "hash999"}

        result = mock_service.find_organization_by_custom_field("mb_id", "test")
        assert result is None

    @responses.activate
    def test_find_organization_by_mb_id(self, mock_service):
        """Test the convenience method for finding by mb_id"""
        mock_service.config.custom_fields = {"org_mb_id": "hash123"}

        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": [{"id": 100, "name": "Test Org", "hash123": "mb-123"}],
                "additional_data": {"pagination": {"more_items_in_collection": False}}
            },
            status=200
        )

        result = mock_service.find_organization_by_mb_id("mb-123")

        assert result is not None
        assert result["id"] == 100

    @responses.activate
    def test_create_organization_with_custom_fields(self, mock_service):
        """Test creating organization with custom fields"""
        mock_service.config.custom_fields = {
            "org_mb_id": "hash123",
            "org_external_id": "hash456"
        }

        responses.add(
            responses.POST,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": {
                    "id": 300,
                    "name": "New Org",
                    "hash123": "mb-new-123",
                    "hash456": "ext-new-456"
                }
            },
            status=200
        )

        org_data = OrganizationData(
            name="New Org",
            custom_fields={
                "mb_id": "mb-new-123",
                "external_id": "ext-new-456"
            }
        )

        result = mock_service.create_organization(org_data)

        assert result is not None
        assert result["id"] == 300
        assert result["name"] == "New Org"

        # Verify request data
        request_body = responses.calls[0].request.body
        request_data = json.loads(request_body.decode('utf-8'))

        assert request_data["name"] == "New Org"
        assert request_data["hash123"] == "mb-new-123"
        assert request_data["hash456"] == "ext-new-456"

    @responses.activate
    def test_create_organization_custom_fields_no_mapping(self, mock_service):
        """Test creating organization when custom field has no mapping"""
        mock_service.config.custom_fields = {"org_other_field": "hash999"}

        responses.add(
            responses.POST,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": {"id": 400, "name": "Test Org"}
            },
            status=200
        )

        org_data = OrganizationData(
            name="Test Org",
            custom_fields={"mb_id": "unmapped-value"}  # No mapping for mb_id
        )

        result = mock_service.create_organization(org_data)

        assert result is not None

        # Verify only name was sent (no unmapped custom fields)
        request_body = responses.calls[0].request.body
        request_data = json.loads(request_body.decode('utf-8'))

        assert request_data["name"] == "Test Org"
        assert len(request_data) == 1  # Only name field

    @responses.activate
    def test_get_or_create_organization_finds_by_mb_id(self, mock_service):
        """Test get_or_create finds existing organization by mb_id"""
        mock_service.config.custom_fields = {"org_mb_id": "hash123"}

        # Mock find_organization_by_mb_id (found)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": [{"id": 500, "name": "Existing Org", "hash123": "existing-mb-123"}],
                "additional_data": {"pagination": {"more_items_in_collection": False}}
            },
            status=200
        )

        org_data = OrganizationData(
            name="Any Name",
            custom_fields={"mb_id": "existing-mb-123"}
        )

        result = mock_service.get_or_create_organization(org_data)

        assert result is not None
        assert result["id"] == 500
        assert result["name"] == "Existing Org"
        assert len(responses.calls) == 1  # Only search call, no create call

    @responses.activate
    def test_get_or_create_organization_creates_when_not_found(self, mock_service):
        """Test get_or_create creates organization when not found by mb_id"""
        mock_service.config.custom_fields = {"org_mb_id": "hash123"}

        # Mock find_organization_by_mb_id (not found)
        responses.add(
            responses.GET,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": [],
                "additional_data": {"pagination": {"more_items_in_collection": False}}
            },
            status=200
        )

        # Mock create_organization
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": {"id": 600, "name": "New Org", "hash123": "new-mb-123"}
            },
            status=200
        )

        org_data = OrganizationData(
            name="New Org",
            custom_fields={"mb_id": "new-mb-123"}
        )

        result = mock_service.get_or_create_organization(org_data)

        assert result is not None
        assert result["id"] == 600
        assert result["name"] == "New Org"
        assert len(responses.calls) == 2  # Search + create calls

    @responses.activate
    def test_get_or_create_organization_no_mb_id_creates_directly(self, mock_service):
        """Test get_or_create creates directly when no mb_id provided"""
        responses.add(
            responses.POST,
            f"{mock_service.base_url}/organizations",
            json={
                "success": True,
                "data": {"id": 700, "name": "No MB ID Org"}
            },
            status=200
        )

        org_data = OrganizationData(name="No MB ID Org")  # No custom_fields

        result = mock_service.get_or_create_organization(org_data)

        assert result is not None
        assert result["id"] == 700
        assert len(responses.calls) == 1  # Only create call, no search


class TestPersonOrganizationLinking:
    """Test linking persons to organizations"""

    @responses.activate
    def test_link_person_to_organization_success(self, mock_service):
        """Test successfully linking person to organization"""
        person_id = 123
        org_id = 456

        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/persons/{person_id}",
            json={
                "success": True,
                "data": {
                    "id": person_id,
                    "name": "Test Person",
                    "org_id": org_id
                }
            },
            status=200
        )

        result = mock_service.link_person_to_organization(person_id, org_id)

        assert result is True

        # Verify request data
        request_body = responses.calls[0].request.body
        request_data = json.loads(request_body.decode('utf-8'))
        assert request_data["org_id"] == org_id

    @responses.activate
    def test_link_person_to_organization_failure(self, mock_service):
        """Test linking person to organization when API fails"""
        person_id = 123
        org_id = 456

        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/persons/{person_id}",
            json={
                "success": False,
                "error": "Person not found"
            },
            status=404
        )

        result = mock_service.link_person_to_organization(person_id, org_id)

        assert result is False

    @responses.activate
    def test_link_person_to_organization_api_error(self, mock_service):
        """Test linking when API returns error"""
        person_id = 123
        org_id = 456

        responses.add(
            responses.PUT,
            f"{mock_service.base_url}/persons/{person_id}",
            json={"error": "Invalid request"},
            status=400
        )

        result = mock_service.link_person_to_organization(person_id, org_id)

        assert result is False


class TestCreateDealWithLinking:
    """Test create_deal method with the new linking functionality"""

    @responses.activate
    def test_create_deal_links_advisor_to_organization(self, mock_service):
        """Test that create_deal links advisor person to organization"""

        # Set up mock service with custom fields (important!)
        mock_service.config.custom_fields = {
            "org_mb_id": "test_hash_123"
        }

        base_url = mock_service.base_url

        # Create sample deal data
        from mb_pipedrive_integration import DealData, PersonData, OrganizationData

        deal_data = DealData(
            title="Test Deal",
            folder_number=12345,
            folder_id="test-folder-123",
            advisor=PersonData(
                name="Test Advisor",
                email="advisor@example.com",
                tags=["ASESOR INMOBILIARIO"]
            ),
            organization=OrganizationData(
                name="Test Organization",
                custom_fields={"mb_id": "org-test-123"}
            )
        )

        # Mock advisor person search (not found)
        responses.add(
            responses.GET,
            f"{base_url}/persons/search",
            json={"success": True, "data": {"items": []}},
            status=200
        )

        # Mock advisor person creation
        responses.add(
            responses.POST,
            f"{base_url}/persons",
            json={"success": True, "data": {"id": 123, "name": "Test Advisor"}},
            status=200
        )

        # Mock organization search by mb_id (not found)
        responses.add(
            responses.GET,
            f"{base_url}/organizations",
            json={
                "success": True,
                "data": [],
                "additional_data": {"pagination": {"more_items_in_collection": False}}
            },
            status=200
        )

        # Mock organization creation
        responses.add(
            responses.POST,
            f"{base_url}/organizations",
            json={"success": True, "data": {"id": 456, "name": "Test Organization"}},
            status=200
        )

        # Mock linking advisor to organization
        responses.add(
            responses.PUT,
            f"{base_url}/persons/123",
            json={
                "success": True,
                "data": {"id": 123, "name": "Test Advisor", "org_id": 456}
            },
            status=200
        )

        # Mock deal creation
        responses.add(
            responses.POST,
            f"{base_url}/deals",
            json={"success": True, "data": {"id": 789, "title": "Test Deal"}},
            status=200
        )

        # Mock notes creation
        responses.add(
            responses.POST,
            f"{base_url}/notes",
            json={"success": True, "data": {"id": 999}},
            status=200
        )

        # Execute the test
        result = mock_service.create_deal(deal_data)

        assert result is not None
        assert result["id"] == 789

        # FIXED: Look for the linking call with proper URL matching
        linking_call = None
        for call in responses.calls:
            if (call.request.method == "PUT" and
                    "/persons/123" in call.request.url):  # Just check if URL contains the path
                linking_call = call
                break

        assert linking_call is not None, f"Person-to-organization linking call not found. Calls made: {[f'{c.request.method} {c.request.url}' for c in responses.calls]}"

        # Verify linking request data
        link_request_data = json.loads(linking_call.request.body.decode('utf-8'))
        assert link_request_data["org_id"] == 456

    # Alternative even simpler approach - just count the PUT calls
    @responses.activate
    def test_create_deal_links_advisor_to_organization_simple(self, mock_service):
        """Test that create_deal makes a PUT call to link person to organization"""

        mock_service.config.custom_fields = {"org_mb_id": "test_hash_123"}

        from mb_pipedrive_integration import DealData, PersonData, OrganizationData

        deal_data = DealData(
            title="Test Deal",
            folder_number=12345,
            folder_id="test-folder-123",
            advisor=PersonData(
                name="Test Advisor",
                email="advisor@example.com",
                tags=["ASESOR INMOBILIARIO"]
            ),
            organization=OrganizationData(
                name="Test Organization",
                custom_fields={"mb_id": "org-test-123"}
            )
        )

        # Mock all responses (same as above but condensed)
        base_url = mock_service.base_url

        responses.add(responses.GET, f"{base_url}/persons/search",
                      json={"success": True, "data": {"items": []}}, status=200)
        responses.add(responses.POST, f"{base_url}/persons",
                      json={"success": True, "data": {"id": 123, "name": "Test Advisor"}}, status=200)
        responses.add(responses.GET, f"{base_url}/organizations",
                      json={"success": True, "data": [],
                            "additional_data": {"pagination": {"more_items_in_collection": False}}}, status=200)
        responses.add(responses.POST, f"{base_url}/organizations",
                      json={"success": True, "data": {"id": 456, "name": "Test Organization"}}, status=200)
        responses.add(responses.PUT, f"{base_url}/persons/123",
                      json={"success": True, "data": {"id": 123, "org_id": 456}}, status=200)
        responses.add(responses.POST, f"{base_url}/deals",
                      json={"success": True, "data": {"id": 789, "title": "Test Deal"}}, status=200)
        responses.add(responses.POST, f"{base_url}/notes",
                      json={"success": True, "data": {"id": 999}}, status=200)

        # Execute
        result = mock_service.create_deal(deal_data)
        assert result is not None

        # SIMPLE CHECK: Just verify that a PUT call was made to persons endpoint
        put_calls = [call for call in responses.calls if call.request.method == "PUT"]
        person_put_calls = [call for call in put_calls if "/persons/" in call.request.url]

        assert len(person_put_calls) == 1, f"Expected 1 person linking call, found {len(person_put_calls)}"

        # Verify the PUT call has the right data
        put_call = person_put_calls[0]
        put_data = json.loads(put_call.request.body.decode('utf-8'))
        assert put_data["org_id"] == 456, f"Expected org_id=456, got {put_data}"

    @responses.activate
    def test_create_deal_no_linking_when_no_advisor(self, mock_service):
        """Test that no linking occurs when there's no advisor"""
        base_url = mock_service.base_url

        # Create deal data without advisor
        from mb_pipedrive_integration import DealData, OrganizationData
        deal_data = DealData(
            title="No Advisor Deal",
            folder_number=123,
            folder_id="test-123",
            organization=OrganizationData(
                name="Test Org",
                custom_fields={"mb_id": "org-123"}
            )
        )

        # Mock organization search (not found)
        responses.add(
            responses.GET,
            f"{base_url}/organizations",
            json={
                "success": True,
                "data": [],
                "additional_data": {"pagination": {"more_items_in_collection": False}}
            },
            status=200
        )

        # Mock organization creation
        responses.add(
            responses.POST,
            f"{base_url}/organizations",
            json={"success": True, "data": {"id": 456, "name": "Test Org"}},
            status=200
        )

        # Mock deal creation
        responses.add(
            responses.POST,
            f"{base_url}/deals",
            json={"success": True, "data": {"id": 789, "title": "No Advisor Deal"}},
            status=200
        )

        # Mock notes creation
        responses.add(
            responses.POST,
            f"{base_url}/notes",
            json={"success": True, "data": {"id": 999}},
            status=200
        )

        result = mock_service.create_deal(deal_data)

        assert result is not None
        assert result["id"] == 789

        # Verify that NO linking call was made
        linking_calls = [call for call in responses.calls
                         if call.request.method == "PUT" and "/persons/" in call.request.url]
        assert len(linking_calls) == 0, "Unexpected linking call made when no advisor present"

    @responses.activate
    def test_create_deal_no_linking_when_no_organization(self, mock_service):
        """Test that no linking occurs when there's no organization"""
        base_url = mock_service.base_url

        # Create deal data without organization
        from mb_pipedrive_integration import DealData, PersonData
        deal_data = DealData(
            title="No Org Deal",
            folder_number=123,
            folder_id="test-123",
            advisor=PersonData(
                name="Test Advisor",
                email="advisor@example.com",
                tags=["ASESOR INMOBILIARIO"]
            )
        )

        # Mock advisor person search (not found)
        responses.add(
            responses.GET,
            f"{base_url}/persons/search",
            json={"success": True, "data": {"items": []}},
            status=200
        )

        # Mock advisor person creation
        responses.add(
            responses.POST,
            f"{base_url}/persons",
            json={"success": True, "data": {"id": 123, "name": "Test Advisor"}},
            status=200
        )

        # Mock deal creation
        responses.add(
            responses.POST,
            f"{base_url}/deals",
            json={"success": True, "data": {"id": 789, "title": "No Org Deal"}},
            status=200
        )

        # Mock notes creation
        responses.add(
            responses.POST,
            f"{base_url}/notes",
            json={"success": True, "data": {"id": 999}},
            status=200
        )

        result = mock_service.create_deal(deal_data)

        assert result is not None
        assert result["id"] == 789

        # Verify that NO linking call was made
        linking_calls = [call for call in responses.calls
                         if call.request.method == "PUT" and "/persons/" in call.request.url]
        assert len(linking_calls) == 0, "Unexpected linking call made when no organization present"

    @responses.activate
    def test_create_deal_continues_when_linking_fails(self, mock_service, sample_deal_data):
        """Test that deal creation continues even if linking fails"""
        base_url = mock_service.base_url

        # Mock all the usual setup calls (persons, organization creation)
        # ... (similar to first test but condensed for brevity)

        # Mock advisor person creation
        responses.add(
            responses.GET,
            f"{base_url}/persons/search",
            json={"success": True, "data": {"items": []}},
            status=200
        )
        responses.add(
            responses.POST,
            f"{base_url}/persons",
            json={"success": True, "data": {"id": 123, "name": "Test Advisor"}},
            status=200
        )

        # Mock organization creation
        responses.add(
            responses.GET,
            f"{base_url}/organizations",
            json={
                "success": True,
                "data": [],
                "additional_data": {"pagination": {"more_items_in_collection": False}}
            },
            status=200
        )
        responses.add(
            responses.POST,
            f"{base_url}/organizations",
            json={"success": True, "data": {"id": 456, "name": "Test Organization"}},
            status=200
        )

        # Mock FAILED linking
        responses.add(
            responses.PUT,
            f"{base_url}/persons/123",
            json={"success": False, "error": "Linking failed"},
            status=400
        )

        # Mock successful deal creation (should still happen)
        responses.add(
            responses.POST,
            f"{base_url}/deals",
            json={"success": True, "data": {"id": 789, "title": "Test Deal"}},
            status=200
        )

        # Mock notes creation
        responses.add(
            responses.POST,
            f"{base_url}/notes",
            json={"success": True, "data": {"id": 999}},
            status=200
        )

        result = mock_service.create_deal(sample_deal_data)

        # Deal should still be created successfully even though linking failed
        assert result is not None
        assert result["id"] == 789