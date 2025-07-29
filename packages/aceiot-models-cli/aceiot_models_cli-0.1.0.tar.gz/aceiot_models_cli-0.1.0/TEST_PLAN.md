# Test Plan for aceiot-models-cli

## Overview
This comprehensive test plan addresses the gaps identified between ace-api-kit functionality and current aceiot-models-cli test coverage.

## Test Categories

### 1. Unit Tests

#### A. API Client Tests (`test_api_client.py` - expand existing)

**Gateway Operations**
```python
# Test cases needed:
- test_get_gateways() - with pagination
- test_get_gateway() - single gateway retrieval
- test_create_gateway() - gateway creation
- test_update_gateway() - gateway updates
- test_create_gateway_token() - token generation
- test_gateway_not_found() - error handling
```

**Point Operations (Complete)**
```python
# Test cases needed:
- test_create_points() - bulk creation
- test_create_points_with_overwrite_tags()
- test_update_point()
- test_get_points() - generic listing
- test_get_point() - single point
- test_get_points_timeseries() - bulk timeseries
- test_get_site_configured_points()
- test_point_batch_size_handling() - test 100+ points
```

**Site Operations (Complete)**
```python
# Test cases needed:
- test_create_site()
- test_get_site_timeseries()
- test_get_site_weather()
- test_site_validation_errors()
```

**DER Event Operations**
```python
# Test cases needed:
- test_get_client_der_events()
- test_create_client_der_events()
- test_update_client_der_events()
- test_get_gateway_der_events()
- test_der_event_filtering()
```

**Advanced Operations**
```python
# Test cases needed:
- test_get_gateway_volttron_agents()
- test_get_gateway_agent_configs()
- test_get_gateway_hawke_configs()
```

#### B. Model Tests (`test_models.py` - new file)

```python
# Test cases for ace-api-kit compatibility:
- test_bacnet_device_normalization()
- test_bacnet_point_serialization()
- test_sample_model_conversion()
- test_hierarchical_path_generation()
- test_model_from_api_response()
```

#### C. CLI Command Tests (expand existing)

**Gateway Commands (`test_gateway_commands.py` - new file)**
```python
# Test cases needed:
- test_gateway_list_command()
- test_gateway_get_command()
- test_gateway_create_command()
- test_gateway_update_command()
- test_gateway_token_command()
```

**Extended Point Commands (`test_point_commands.py` - expand)**
```python
# Test cases needed:
- test_points_create_command()
- test_points_update_command()
- test_points_bulk_timeseries_command()
- test_points_configured_list_command()
```

**DER Event Commands (`test_der_commands.py` - new file)**
```python
# Test cases needed:
- test_der_events_list_command()
- test_der_events_create_command()
- test_der_events_update_command()
```

### 2. Integration Tests (`tests/integration/` - new directory)

#### A. End-to-End Workflows (`test_e2e_workflows.py`)

```python
# Test scenarios:
- test_complete_site_setup_workflow()
  # Create client -> Create site -> Create gateway -> Create points
  
- test_data_collection_workflow()
  # Configure points -> Enable collection -> Retrieve timeseries
  
- test_bacnet_discovery_workflow()
  # Get discovered points -> Convert to configured -> Enable collection
  
- test_bulk_operations_workflow()
  # Create 500+ points -> Batch retrieve timeseries
```

#### B. Authentication Tests (`test_authentication.py`)

```python
# Test cases:
- test_api_key_authentication()
- test_invalid_api_key_handling()
- test_token_expiration_handling()
- test_bearer_token_format()
```

#### C. Error Recovery Tests (`test_error_recovery.py`)

```python
# Test cases:
- test_network_timeout_retry()
- test_rate_limiting_handling()
- test_partial_batch_failure_recovery()
- test_pagination_error_recovery()
```

### 3. Performance Tests (`tests/performance/` - new directory)

#### A. Load Tests (`test_load.py`)

```python
# Test cases:
- test_bulk_point_creation_performance()
- test_large_timeseries_retrieval()
- test_concurrent_api_requests()
- test_pagination_performance()
```

#### B. Memory Tests (`test_memory.py`)

```python
# Test cases:
- test_large_dataset_memory_usage()
- test_streaming_response_handling()
- test_batch_processing_memory_efficiency()
```

### 4. BACnet-Specific Tests (`tests/bacnet/` - new directory)

#### A. Device Tests (`test_bacnet_devices.py`)

```python
# Test cases:
- test_device_address_normalization()
- test_device_path_serialization()
- test_device_discovery()
- test_device_property_extraction()
```

#### B. Point Tests (`test_bacnet_points.py`)

```python
# Test cases:
- test_bacnet_point_types()
- test_point_unit_handling()
- test_raw_property_preservation()
- test_present_value_updates()
```

## Test Data Requirements

### Fixtures Needed

```python
# conftest.py additions:
@pytest.fixture
def sample_bacnet_device():
    """BACnet device test data"""

@pytest.fixture
def sample_der_event():
    """DER event test data"""

@pytest.fixture
def bulk_points_data():
    """Large dataset for performance testing"""

@pytest.fixture
def mock_api_responses():
    """Comprehensive API response mocks"""
```

## Test Execution Strategy

### Phase 1: Critical Functionality (Week 1-2)
1. Gateway CRUD operations
2. Complete point operations
3. Basic BACnet support

### Phase 2: Advanced Features (Week 3-4)
1. DER event management
2. Volttron/Agent configurations
3. Bulk operations

### Phase 3: Integration & Performance (Week 5-6)
1. End-to-end workflows
2. Performance benchmarks
3. Error recovery scenarios

## Coverage Goals

- **Unit Test Coverage**: 90%+
- **Integration Test Coverage**: 80%+
- **Critical Path Coverage**: 100%
- **Edge Case Coverage**: 75%+

## Test Environment Requirements

1. **Mock API Server**: For integration tests without hitting production
2. **Test Database**: For data persistence tests
3. **Performance Monitoring**: Tools to measure response times and memory
4. **CI/CD Integration**: Automated test runs on all commits

## Success Criteria

1. All identified gaps from ace-api-kit are covered
2. No regression in existing functionality
3. Performance benchmarks established
4. Documentation updated with test examples
5. CI pipeline includes all test suites