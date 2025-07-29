# Missing Features in aceiot-models-cli vs ace-api-kit

## Summary
This document outlines the features present in ace-api-kit that are missing from aceiot-models-cli.

## Core Missing Features

### 1. BACnet-Specific Support
- **BACnetDevice Model**: Device normalization, address handling, and path serialization
- **BACnetPoint Model**: Full BACnet point support with device relationships
- **Discovered Points Endpoint**: `/sites/{site}/points` for discovered BACnet points
- **Device Address Normalization**: Translation and standardization of device addresses

### 2. Data Processing & Transformation
- **Model Conversion Methods**: `from_api_model()` classmethods for deserializing API responses
- **Hierarchical Path Serialization**: Creating paths like `client/site/device/point`
- **Automatic Response-to-Model Conversion**: Converting API responses to typed objects
- **Raw Property Extraction**: Extracting BACnet raw properties from API responses

### 3. Advanced API Features
- **Automatic Pagination**: `get_api_results()` with automatic page iteration
- **Batch Processing**: Automatic batching of large requests (e.g., 100 points at a time)
- **Generic API Helpers**: `post_to_api()` and `get_api_results()` utilities
- **JWT Authentication**: Direct JWT token support vs API key

### 4. Model Support Gaps
- **Sample Model**: Simple timeseries sample representation
- **Full Model Classes**: Only Create/Update variants used, missing complete models with all fields
- **Model Methods**: Missing serialization, normalization, and utility methods on models

## Implementation Priority

### High Priority
1. Add BACnet support (models and endpoints)
2. Implement discovered points endpoint
3. Add model conversion methods for API responses
4. Implement batch processing for bulk operations

### Medium Priority
1. Add generic API helper utilities
2. Implement automatic pagination
3. Add full model classes (not just Create/Update)
4. Support hierarchical path serialization

### Low Priority
1. JWT authentication support (if needed)
2. Raw property extraction utilities
3. Additional model utility methods

## Notes
- aceiot-models-cli has broader API coverage but lacks specialized data handling
- ace-api-kit focuses on data retrieval and transformation
- Both packages serve different use cases but should be aligned for consistency