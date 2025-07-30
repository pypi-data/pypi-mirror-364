# Volttron Agent Deployment User Flow

## Overview
This document outlines the user flow for deploying Volttron agents to ACE IoT gateways through the Aerodrome Cloud API. The workflow consists of three main steps that must be executed in sequence.

## User Journey

### 1. Package Preparation Phase
**User Goal**: Prepare a Volttron agent directory for deployment

**User Actions**:
- Develop/modify Volttron agent code locally
- Create agent configuration file (JSON/YAML)
- Organize files in standard Volttron agent directory structure

**System Requirements**:
- Validate directory structure
- Check for required files (setup.py, agent.py, etc.)
- Ensure configuration file is valid JSON/YAML

### 2. Upload Phase

#### 2.1 Upload Agent Package
**User Goal**: Upload the agent directory as a zip file

**User Actions**:
- Select agent directory to upload
- Optionally specify agent name/version
- Initiate upload

**System Actions**:
- Automatically zip the directory (if not already zipped)
- Upload to `/volttron_agents` endpoint
- Return package ID/reference for later use
- Show upload progress for large files

**Success Indicators**:
- Package ID returned
- Confirmation message displayed
- Package visible in listing

#### 2.2 Upload Configuration
**User Goal**: Upload agent configuration file

**User Actions**:
- Select configuration file
- Specify configuration name (optional)
- Link to agent identity

**System Actions**:
- Validate configuration format
- Upload to `/agent_configs` endpoint
- Return configuration ID/reference
- Associate with user's account/gateway

**Success Indicators**:
- Configuration ID returned
- Validation passed message
- Configuration visible in listing

### 3. Deployment Phase
**User Goal**: Deploy the agent package with configuration to a gateway

**User Actions**:
- Select target gateway
- Reference uploaded package ID
- Reference configuration ID
- Optionally set deployment parameters (auto-start, priority, etc.)
- Initiate deployment

**System Actions**:
- Validate package and config compatibility
- Push to `/volttron_agent_config_packages` endpoint
- Deploy to specified gateway
- Monitor deployment status

**Success Indicators**:
- Deployment ID returned
- Status updates (queued → deploying → deployed)
- Agent appears in gateway's agent list
- Agent status shows as running

## Error Handling

### Common Error Scenarios:
1. **Invalid Directory Structure**
   - User Feedback: Clear message about missing required files
   - Recovery: Provide template/example structure

2. **Configuration Validation Failure**
   - User Feedback: Specific validation errors with line numbers
   - Recovery: Offer to edit configuration inline

3. **Upload Failures**
   - User Feedback: Network/size/permission error messages
   - Recovery: Resume capability for large files

4. **Deployment Conflicts**
   - User Feedback: Existing agent version warning
   - Recovery: Option to force update or create new version

5. **Gateway Offline**
   - User Feedback: Gateway status indication
   - Recovery: Queue deployment for when gateway comes online

## User Experience Principles

1. **Progressive Disclosure**: Don't overwhelm users with all options upfront
2. **Smart Defaults**: Pre-fill common values, auto-detect agent names
3. **Clear Feedback**: Always show what's happening and what's next
4. **Graceful Degradation**: Work offline where possible, sync when connected
5. **Idempotency**: Allow re-running commands safely

## State Management

The system should track:
- Uploaded packages (with metadata)
- Uploaded configurations
- Deployment history
- Gateway status
- Agent running status

Users should be able to:
- List all uploaded packages/configs
- Check deployment status
- Rollback deployments
- View agent logs