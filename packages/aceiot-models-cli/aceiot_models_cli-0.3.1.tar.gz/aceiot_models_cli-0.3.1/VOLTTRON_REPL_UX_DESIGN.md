# Volttron REPL Interactive Workflow Design

## Overview
The REPL mode provides an interactive, context-aware environment for deploying Volttron agents. It guides users through the deployment process with smart defaults and helpful prompts.

## REPL Context Extensions

### New Context Type: `volttron`
Add a new context type to the existing client/site/gateway hierarchy:

```
aceiot> use volttron
aceiot(volttron)>
```

## Interactive Workflows

### 1. Guided Deployment Workflow
```
aceiot> volttron deploy

Welcome to Volttron Agent Deployment!
This wizard will guide you through deploying an agent to a gateway.

Step 1: Select or upload agent package
  1) Upload new agent package
  2) Use existing package
  
Choice [1-2]: 1

Enter path to agent directory or zip file: ./weather-agent/
✓ Found agent directory: weather-agent
✓ Detected setup.py
  - Name: WeatherAgent
  - Version: 2.0.1
  
Use detected values? [Y/n]: y

Creating package archive...
[████████████████████████████████████] 100% Complete

✓ Package uploaded successfully!
  Package ID: pkg_w34h89sf
  Size: 2.3 MB

Step 2: Select or upload configuration
  1) Upload new configuration
  2) Use existing configuration
  3) Skip (use default configuration)
  
Choice [1-3]: 1

Enter path to configuration file: ./config/prod.json
✓ Configuration validated

Upload this configuration? [Y/n]: y
✓ Configuration uploaded successfully!
  Config ID: cfg_m92kd83j

Step 3: Select target gateway
             Available Gateways              
+------+-------------+--------+-------------+
| #    | Name        | Status | Site        |
+------+-------------+--------+-------------+
| 1    | gw-prod-01  | Online | central-hq  |
| 2    | gw-prod-02  | Online | central-hq  |
| 3    | gw-test-01  | Online | test-lab    |
+------+-------------+--------+-------------+

Enter number (1-3) or gateway name: 1

Step 4: Deployment options
Auto-start agent after deployment? [Y/n]: y
Agent priority (1-10) [5]: 8

Ready to deploy:
  Agent: WeatherAgent v2.0.1
  Config: prod.json
  Gateway: gw-prod-01
  Options: auto-start=yes, priority=8
  
Proceed with deployment? [Y/n]: y

Deploying...
✓ Deployment initiated
✓ Package transferred to gateway
✓ Agent installed
✓ Configuration applied
✓ Agent started

Deployment successful!
Agent is now running on gw-prod-01
```

### 2. Context-Aware Commands
When in volttron context:

```
aceiot(volttron)> list packages
                    Your Agent Packages                     
+------+---------------+---------+------+------------------+
| #    | Package ID    | Name    | Ver. | Uploaded         |
+------+---------------+---------+------+------------------+
| 1    | pkg_w34h89sf  | Weather | 2.0.1| 5 minutes ago    |
| 2    | pkg_k92jd73h  | BACnet  | 1.2.0| 2 hours ago      |
| 3    | pkg_m83ks92j  | Modbus  | 1.0.0| Yesterday        |
+------+---------------+---------+------+------------------+

aceiot(volttron)> use package 1
aceiot(volttron:pkg_w34h89sf)> info

Package Details:
  ID: pkg_w34h89sf
  Name: WeatherAgent
  Version: 2.0.1
  Size: 2.3 MB
  Uploaded: 2025-07-23T15:30:00Z
  Description: Collects weather data from external APIs
  
  Files:
    - weather_agent/
      - __init__.py
      - agent.py
      - setup.py
      - requirements.txt

aceiot(volttron:pkg_w34h89sf)> deploy

Select configuration:
  1) prod.json (cfg_m92kd83j)
  2) test.json (cfg_k92js83k)
  3) Upload new configuration
  
Choice [1-3]: 1

Select gateway (or press Enter to list): [Enter]
[... gateway selection ...]
```

### 3. Quick Commands in Volttron Context

```
aceiot(volttron)> upload ./my-agent.zip
Uploading agent package...
✓ Package uploaded: pkg_j93ks92j

aceiot(volttron)> upload-config ./config.yaml
✓ Configuration uploaded: cfg_m92js93k

aceiot(volttron)> deploy pkg_j93ks92j cfg_m92js93k gw-prod-01
✓ Deployment successful: dep_k92js93k

aceiot(volttron)> status dep_k92js93k
Deployment Status:
  ID: dep_k92js93k
  Agent: MyAgent v1.0.0
  Gateway: gw-prod-01
  Status: Running
  Uptime: 2 minutes
  
aceiot(volttron)> logs gw-prod-01 my.agent
[2025-07-23 15:40:00] Agent started successfully
[2025-07-23 15:40:01] Connected to message bus
[2025-07-23 15:40:02] Subscribing to topics...
```

### 4. Gateway Context Extension
When in gateway context, add volttron-specific commands:

```
aceiot(gw:gw-prod-01)> volttron agents
                Running Volttron Agents                
+------+------------------+---------+--------+--------+
| #    | Identity         | Name    | Ver.   | Status |
+------+------------------+---------+--------+--------+
| 1    | weather.agent    | Weather | 2.0.1  | Running|
| 2    | bacnet.agent     | BACnet  | 1.2.0  | Running|
| 3    | modbus.agent     | Modbus  | 1.0.0  | Stopped|
+------+------------------+---------+--------+--------+

aceiot(gw:gw-prod-01)> volttron restart 3
Restarting modbus.agent...
✓ Agent restarted successfully

aceiot(gw:gw-prod-01)> volttron deploy
[Starts deployment workflow with gateway pre-selected]
```

### 5. Smart Tab Completion

```
aceiot(volttron)> deploy pkg_[TAB]
pkg_w34h89sf  pkg_k92jd73h  pkg_m83ks92j

aceiot(volttron)> deploy pkg_w34h89sf cfg_[TAB]
cfg_m92kd83j  cfg_k92js83k  cfg_j93ks82j

aceiot(volttron)> deploy pkg_w34h89sf cfg_m92kd83j gw-[TAB]
gw-prod-01  gw-prod-02  gw-test-01
```

### 6. Inline Help
```
aceiot(volttron)> help deploy

volttron deploy - Deploy an agent package to a gateway

Usage:
  deploy                           # Interactive deployment wizard
  deploy <pkg> <cfg> <gateway>     # Direct deployment
  
Options in interactive mode:
  - Step-by-step guidance
  - Validation at each step
  - Option to save deployment configuration
  
Examples:
  deploy
  deploy pkg_123 cfg_456 gw-prod-01
  
Related commands:
  upload          - Upload agent package
  upload-config   - Upload configuration
  list packages   - Show uploaded packages
  list configs    - Show uploaded configurations
```

### 7. Error Recovery in REPL
```
aceiot(volttron)> deploy pkg_invalid cfg_123 gw-01

Error: Package 'pkg_invalid' not found

Did you mean one of these?
  - pkg_w34h89sf (WeatherAgent v2.0.1)
  - pkg_k92jd73h (BACnetAgent v1.2.0)
  
Or upload a new package:
  volttron upload <path-to-agent>
```

### 8. Batch Operations
```
aceiot(volttron)> batch-deploy

Batch Deployment Mode
Enter deployments (empty line to finish):

Deployment 1:
  Package ID: pkg_123
  Config ID: cfg_456
  Gateway: gw-prod-01
  
Add another? [Y/n]: y

Deployment 2:
  Package ID: pkg_123
  Config ID: cfg_789
  Gateway: gw-prod-02
  
Add another? [Y/n]: n

Ready to deploy 2 agents. Continue? [Y/n]: y

Deploying to gw-prod-01... ✓
Deploying to gw-prod-02... ✓

All deployments completed successfully!
```

### 9. History and Shortcuts
The REPL remembers recent operations:

```
aceiot(volttron)> recent
Recent Operations:
  1. deploy pkg_w34h89sf cfg_m92kd83j gw-prod-01 (2 min ago)
  2. upload ./weather-agent/ (5 min ago)
  3. upload-config ./config/prod.json (4 min ago)
  
Repeat operation (1-3) or press Enter to skip: 1

Repeating: deploy pkg_w34h89sf cfg_m92kd83j gw-prod-01
Proceed? [Y/n]: 
```

### 10. State Persistence
Save deployment configurations for reuse:

```
aceiot(volttron)> save-deployment weather-prod

Saved current deployment configuration as 'weather-prod':
  Package: pkg_w34h89sf (WeatherAgent v2.0.1)
  Config: cfg_m92kd83j (prod.json)
  Gateway: gw-prod-01
  Options: auto-start=yes, priority=8

aceiot(volttron)> deploy --saved weather-prod
Loading saved deployment 'weather-prod'...
✓ Deployment successful
```

## Integration with Existing REPL Features

1. **Context Hierarchy**: volttron context can be entered from any level
2. **Back Navigation**: `back` command works to exit volttron context
3. **Clear Command**: Works as expected
4. **Output Formats**: Respect global output format settings
5. **Error Handling**: Consistent with existing error display

## User Experience Principles

1. **Progressive Disclosure**: Start simple, reveal complexity as needed
2. **Intelligent Defaults**: Pre-select most likely options
3. **Continuous Feedback**: Always show progress and status
4. **Error Prevention**: Validate early and often
5. **Easy Recovery**: Allow users to go back and correct mistakes