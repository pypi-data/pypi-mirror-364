# New Use Cases from ace-api-kit

## Overview
This document outlines new use cases and scenarios implied by the ace-api-kit codebase that should be supported in aceiot-models-cli.

## 1. BACnet Device Discovery and Management

### Use Case: Building System Discovery
**Description**: Automatically discover BACnet devices and points in a building network
**Requirements**:
- Support for discovered vs configured points distinction
- Device address normalization for consistent identification
- Hierarchical device/point naming (client/site/device/point)

### Use Case: BACnet Device Inventory
**Description**: Maintain an inventory of all BACnet devices with their properties
**Requirements**:
- Store device ID, address, name, and description
- Track last seen and last scanned timestamps
- Support proxy ID for device communication

## 2. Bulk Data Operations

### Use Case: Large-Scale Timeseries Retrieval
**Description**: Retrieve timeseries data for hundreds or thousands of points efficiently
**Requirements**:
- Automatic batching (100 points per request)
- Progress indication for long-running operations
- Memory-efficient processing for large datasets

### Use Case: Site-Wide Data Collection
**Description**: Collect all timeseries data for an entire site
**Requirements**:
- Site-level timeseries endpoint support
- Efficient handling of multiple point types
- Aggregation of data from multiple sources

## 3. Data Transformation and Normalization

### Use Case: Cross-Platform Device Integration
**Description**: Normalize device addresses and names across different BACnet implementations
**Requirements**:
- Address translation mapping (underscores to dots, remove commas)
- Consistent device path serialization
- Support for various device naming conventions

### Use Case: API Response Processing
**Description**: Convert raw API responses into structured, typed objects
**Requirements**:
- Model factory methods for API deserialization
- Type-safe data handling
- Automatic datetime parsing

## 4. Advanced Querying and Filtering

### Use Case: Point Discovery by Type
**Description**: Find all points of a specific type across sites
**Requirements**:
- Filter by object type (analog input, binary output, etc.)
- Filter by point properties (units, description)
- Support for marker and key-value tags

### Use Case: Device-Specific Point Queries
**Description**: Get all points associated with a specific device
**Requirements**:
- Device-to-point relationship mapping
- Efficient querying by device ID or address
- Include device metadata in point responses

## 5. Real-Time Data Monitoring

### Use Case: Live Point Value Monitoring
**Description**: Monitor present values of BACnet points in real-time
**Requirements**:
- Access to present_value field
- Support for different data types (numeric, boolean, string)
- Efficient polling or subscription mechanisms

### Use Case: Change Detection
**Description**: Detect when point values or configurations change
**Requirements**:
- Track created and updated timestamps
- Compare current vs previous values
- Alert on significant changes

## 6. Integration Scenarios

### Use Case: Building Management System Integration
**Description**: Integrate with existing BMS platforms
**Requirements**:
- Support for standard BACnet object types
- Preserve raw BACnet properties
- Compatible data formatting

### Use Case: Energy Management Integration
**Description**: Collect and analyze energy-related data points
**Requirements**:
- Identify energy-related points by tags or type
- Support for various unit conversions
- Time-series aggregation capabilities

## 7. Configuration Management

### Use Case: Point Configuration Deployment
**Description**: Deploy point configurations across multiple sites
**Requirements**:
- Differentiate configured vs discovered points
- Support collect_enabled and collect_interval settings
- Batch configuration updates

### Use Case: Gateway Configuration Management
**Description**: Manage gateway configurations and deployment settings
**Requirements**:
- Access to deploy_config and interfaces
- Track configuration versions and updates
- Support for multiple gateway types

## Testing Requirements

For each use case above, tests should cover:
1. Normal operation (happy path)
2. Error conditions (network failures, invalid data)
3. Edge cases (empty results, maximum limits)
4. Performance characteristics (large datasets)
5. Data integrity (correct transformations)

## Priority Matrix

| Use Case Category | Priority | Complexity | Business Value |
|-------------------|----------|------------|----------------|
| BACnet Device Discovery | High | High | Critical |
| Bulk Data Operations | High | Medium | High |
| Data Transformation | Medium | Low | Medium |
| Advanced Querying | Medium | Medium | Medium |
| Real-Time Monitoring | Low | High | Medium |
| Integration Scenarios | Medium | Medium | High |
| Configuration Management | High | Low | High |