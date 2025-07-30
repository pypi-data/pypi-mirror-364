# Volttron CLI Command Structure Design

## Command Hierarchy

### Main Command Group: `volttron`
All Volttron-related commands will be grouped under a main `volttron` command to keep them organized and discoverable.

```bash
aceiot-models-cli volttron [COMMAND] [OPTIONS]
```

## Commands

### 1. Upload Agent Package
```bash
aceiot-models-cli volttron upload-agent [PATH] [OPTIONS]
```

**Arguments**:
- `PATH`: Path to agent directory or zip file (required)

**Options**:
- `--name, -n`: Agent package name (auto-detected from setup.py if not provided)
- `--version, -v`: Agent version (auto-detected from setup.py if not provided)
- `--description, -d`: Package description
- `--zip/--no-zip`: Force zip or assume already zipped (default: auto-detect)
- `--output, -o`: Output format (json, table)

**Examples**:
```bash
# Upload from directory (auto-zips)
aceiot-models-cli volttron upload-agent ./my-agent/

# Upload existing zip file
aceiot-models-cli volttron upload-agent ./my-agent.zip

# Upload with explicit name and version
aceiot-models-cli volttron upload-agent ./my-agent/ --name "WeatherAgent" --version "2.0.1"
```

**Output**:
```
Preparing agent package...
✓ Directory structure validated
✓ Creating zip archive (2.3 MB)
✓ Uploading to Aerodrome Cloud...

Agent package uploaded successfully!
Package ID: pkg_w34h89sf
Name: WeatherAgent
Version: 2.0.1
Size: 2.3 MB
Upload time: 2025-07-23T15:30:00Z
```

### 2. Upload Configuration
```bash
aceiot-models-cli volttron upload-config [FILE] [OPTIONS]
```

**Arguments**:
- `FILE`: Path to configuration file (JSON/YAML)

**Options**:
- `--name, -n`: Configuration name (defaults to filename)
- `--agent-identity, -a`: Associated agent identity
- `--validate/--no-validate`: Validate configuration before upload (default: validate)
- `--output, -o`: Output format (json, table)

**Examples**:
```bash
# Upload configuration file
aceiot-models-cli volttron upload-config ./config/weather-agent.json

# Upload with specific name and agent identity
aceiot-models-cli volttron upload-config ./config.yaml --name "prod-config" --agent-identity "weather.agent"
```

**Output**:
```
Validating configuration...
✓ Configuration valid

Uploading configuration...
✓ Configuration uploaded successfully!

Config ID: cfg_m92kd83j
Name: prod-config
Agent Identity: weather.agent
Size: 4.2 KB
Upload time: 2025-07-23T15:32:00Z
```

### 3. Deploy Package
```bash
aceiot-models-cli volttron deploy [OPTIONS]
```

**Options**:
- `--package-id, -p`: Package ID from upload (required)
- `--config-id, -c`: Configuration ID from upload (required)
- `--gateway, -g`: Target gateway name (required)
- `--auto-start/--no-auto-start`: Start agent after deployment (default: auto-start)
- `--priority`: Agent priority (1-10, default: 5)
- `--force`: Force deployment even if agent exists
- `--output, -o`: Output format (json, table)

**Examples**:
```bash
# Basic deployment
aceiot-models-cli volttron deploy --package-id pkg_w34h89sf --config-id cfg_m92kd83j --gateway gw-prod-01

# Deployment with options
aceiot-models-cli volttron deploy -p pkg_w34h89sf -c cfg_m92kd83j -g gw-prod-01 --priority 8 --force
```

**Output**:
```
Initiating deployment...
Gateway: gw-prod-01
Package: WeatherAgent v2.0.1
Configuration: prod-config

✓ Package validated
✓ Configuration validated
✓ Gateway online
✓ Deployment initiated

Deployment ID: dep_k38sh29d
Status: QUEUED → DEPLOYING → DEPLOYED

Agent deployed successfully!
Agent Identity: weather.agent
Status: Running
Started: 2025-07-23T15:35:00Z
```

### 4. One-Step Deploy (Convenience Command)
```bash
aceiot-models-cli volttron quick-deploy [PATH] [CONFIG] [GATEWAY] [OPTIONS]
```

**Arguments**:
- `PATH`: Path to agent directory or zip
- `CONFIG`: Path to configuration file
- `GATEWAY`: Target gateway name

**Options**:
- All options from upload-agent, upload-config, and deploy commands
- `--skip-validation`: Skip validation steps for faster deployment

**Example**:
```bash
# Deploy in one command
aceiot-models-cli volttron quick-deploy ./weather-agent/ ./config.json gw-prod-01
```

### 5. List Commands
```bash
# List uploaded packages
aceiot-models-cli volttron list-packages [OPTIONS]

# List configurations
aceiot-models-cli volttron list-configs [OPTIONS]

# List deployments
aceiot-models-cli volttron list-deployments [OPTIONS]
```

**Common Options**:
- `--page`: Page number
- `--per-page`: Items per page
- `--filter`: Filter expression
- `--sort`: Sort field
- `--output, -o`: Output format

### 6. Status and Management
```bash
# Check deployment status
aceiot-models-cli volttron deployment-status [DEPLOYMENT_ID]

# Get agent logs
aceiot-models-cli volttron agent-logs [GATEWAY] [AGENT_IDENTITY] [OPTIONS]

# Stop/start/restart agent
aceiot-models-cli volttron agent-control [GATEWAY] [AGENT_IDENTITY] [start|stop|restart]

# Delete package/config
aceiot-models-cli volttron delete-package [PACKAGE_ID]
aceiot-models-cli volttron delete-config [CONFIG_ID]
```

## Error Messages

### Helpful Error Format
```
Error: Configuration validation failed

  Problem: Missing required field 'agent_identity' in configuration
  Location: config.json, line 5
  
  Fix: Add an 'agent_identity' field to your configuration:
  
    {
      "agent_identity": "your.agent.name",
      ...
    }
  
  Documentation: https://docs.aceiot.cloud/volttron/config
```

## Progress Indicators

For long operations, show progress:
```
Uploading agent package (15.2 MB)
[████████████████████░░░░░░░░░░░░░░░░] 48% | 7.3 MB/15.2 MB | 245 KB/s | ETA: 32s
```

## Interactive Features

### Auto-completion
- Gateway names from `gateways list`
- Package/config IDs from recent uploads
- Agent identities from current deployments

### Confirmation Prompts
```bash
aceiot-models-cli volttron deploy --force -p pkg_123 -c cfg_456 -g gw-01

Warning: Agent 'weather.agent' already exists on gateway 'gw-01'
This will replace the existing agent and its configuration.

Current version: 1.0.0 (running)
New version: 2.0.1

Continue? [y/N]:
```

## Configuration File Support

Users can create `.volttron-deploy.yaml` files:
```yaml
agent:
  name: WeatherAgent
  version: 2.0.1
  path: ./src/
  
config:
  path: ./config/production.json
  
deployment:
  gateway: gw-prod-01
  auto_start: true
  priority: 8
```

Then deploy with:
```bash
aceiot-models-cli volttron deploy --from-file .volttron-deploy.yaml
```