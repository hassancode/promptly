"""
OpenAPI contract validation tests

Validates that:
1. OpenAPI specification is syntactically valid
2. All schemas are properly defined
3. All endpoints have required fields
4. Response schemas match specification
"""
import pytest
import yaml
from pathlib import Path
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename


# Path to OpenAPI specification
OPENAPI_SPEC_PATH = Path(__file__).parent.parent.parent.parent.parent / "specs" / "001-ai-visibility-platform" / "contracts" / "openapi.yaml"


def test_openapi_spec_exists():
    """Test that OpenAPI specification file exists"""
    assert OPENAPI_SPEC_PATH.exists(), f"OpenAPI spec not found at {OPENAPI_SPEC_PATH}"


def test_openapi_spec_is_valid_yaml():
    """Test that OpenAPI specification is valid YAML"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        try:
            spec = yaml.safe_load(f)
            assert spec is not None
            assert isinstance(spec, dict)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML: {e}")


def test_openapi_spec_is_valid():
    """Test that OpenAPI specification is valid according to OpenAPI 3.0 standard"""
    spec_dict, spec_url = read_from_filename(str(OPENAPI_SPEC_PATH))

    try:
        validate_spec(spec_dict)
    except Exception as e:
        pytest.fail(f"OpenAPI spec validation failed: {e}")


def test_openapi_has_required_metadata():
    """Test that OpenAPI spec has required metadata fields"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    assert "openapi" in spec, "Missing 'openapi' version field"
    assert spec["openapi"].startswith("3.0"), "Must be OpenAPI 3.0 specification"
    assert "info" in spec, "Missing 'info' section"
    assert "title" in spec["info"], "Missing title in info section"
    assert "version" in spec["info"], "Missing version in info section"


def test_openapi_has_servers():
    """Test that OpenAPI spec defines servers"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    assert "servers" in spec, "Missing 'servers' section"
    assert len(spec["servers"]) > 0, "At least one server must be defined"

    for server in spec["servers"]:
        assert "url" in server, "Server must have URL"
        assert "description" in server, "Server should have description"


def test_openapi_has_authentication_endpoints():
    """Test that authentication endpoints are defined"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})

    # Required authentication endpoints
    required_auth_endpoints = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/auth/me",
    ]

    for endpoint in required_auth_endpoints:
        assert endpoint in paths, f"Missing required endpoint: {endpoint}"


def test_openapi_has_analysis_endpoints():
    """Test that analysis endpoints are defined"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})

    # Required analysis endpoints
    required_analysis_endpoints = [
        "/api/v1/analyses",
        "/api/v1/analyses/{analysisId}/start",
    ]

    for endpoint in required_analysis_endpoints:
        assert endpoint in paths, f"Missing required endpoint: {endpoint}"


def test_openapi_has_insights_endpoints():
    """Test that insights endpoints are defined"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})

    # Required insights endpoints
    assert "/api/v1/analyses/{analysisId}/insights/generate" in paths, \
        "Missing insights generation endpoint"


def test_openapi_endpoints_have_operation_ids():
    """Test that all endpoints have unique operation IDs"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})
    operation_ids = []

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                assert "operationId" in operation, \
                    f"Missing operationId for {method.upper()} {path}"

                op_id = operation["operationId"]
                assert op_id not in operation_ids, \
                    f"Duplicate operationId: {op_id}"
                operation_ids.append(op_id)


def test_openapi_endpoints_have_tags():
    """Test that all endpoints are tagged for organization"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                assert "tags" in operation, \
                    f"Missing tags for {method.upper()} {path}"
                assert len(operation["tags"]) > 0, \
                    f"Empty tags for {method.upper()} {path}"


def test_openapi_has_security_schemes():
    """Test that security schemes are defined"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    assert "components" in spec, "Missing 'components' section"
    assert "securitySchemes" in spec["components"], \
        "Missing 'securitySchemes' in components"

    assert "cookieAuth" in spec["components"]["securitySchemes"], \
        "Missing 'cookieAuth' security scheme"


def test_openapi_has_error_schemas():
    """Test that error response schemas are defined"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    components = spec.get("components", {})
    schemas = components.get("schemas", {})
    responses = components.get("responses", {})

    # Check for error response schema
    assert "ErrorResponse" in schemas, "Missing 'ErrorResponse' schema"

    # Check for common error responses
    assert "BadRequest" in responses, "Missing 'BadRequest' response"
    assert "Unauthorized" in responses, "Missing 'Unauthorized' response"


def test_openapi_schemas_have_required_fields():
    """Test that request/response schemas define required fields"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    schemas = spec.get("components", {}).get("schemas", {})

    # Schemas that must have 'required' field
    schemas_with_required = [
        "RegisterRequest",
        "LoginRequest",
        "AnalysisCreateRequest",
    ]

    for schema_name in schemas_with_required:
        assert schema_name in schemas, f"Missing schema: {schema_name}"
        assert "required" in schemas[schema_name], \
            f"Schema '{schema_name}' must define required fields"
        assert len(schemas[schema_name]["required"]) > 0, \
            f"Schema '{schema_name}' required array is empty"


def test_openapi_responses_have_status_codes():
    """Test that endpoints define response status codes"""
    with open(OPENAPI_SPEC_PATH, "r") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                assert "responses" in operation, \
                    f"Missing responses for {method.upper()} {path}"

                responses = operation["responses"]
                assert len(responses) > 0, \
                    f"Empty responses for {method.upper()} {path}"

                # Check for at least one success response (2xx)
                success_codes = [code for code in responses.keys()
                                if code.startswith("2")]
                assert len(success_codes) > 0, \
                    f"No success response for {method.upper()} {path}"
