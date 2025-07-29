# ACE IoT Models CLI - REPL Mode UX Specification

## Overview

This document specifies the user experience design for the interactive REPL (Read-Eval-Print Loop) mode of the aceiot-models-cli. The REPL mode provides an immersive, context-aware shell environment for exploring and managing ACE IoT data.

## 1. User Journey Maps

### 1.1 Typical User Workflows

#### Developer Exploration Workflow
```
Start REPL → Authenticate → Explore Clients → Navigate to Site → 
Examine Points → Query Timeseries → Export Data → Exit
```

#### Operations Monitoring Workflow
```
Start REPL → Set Context to Client → Monitor Gateways → 
Check Status → Set Alerts → Switch to Another Site → Exit
```

#### Data Analysis Workflow
```
Start REPL → Navigate to Site → List Points → Filter by Type → 
Batch Query Timeseries → Export to File → Statistical Analysis → Exit
```

#### Configuration Management Workflow
```
Start REPL → Navigate to Gateway → View Configs → Update Settings → 
Test Changes → Apply Changes → Verify Status → Exit
```

### 1.2 Entry Points

#### From CLI
```bash
# Direct REPL entry
aceiot-models repl

# REPL with initial context
aceiot-models repl --client "acme-corp"
aceiot-models repl --site "building-a"
aceiot-models repl --gateway "gw-001"

# REPL with specific configuration
aceiot-models repl --config ~/.aceiot/prod.yaml --output json
```

#### Auto-REPL Triggers
- When complex multi-step operations are detected
- When user requests exploration mode
- When batch operations require user confirmation

### 1.3 Context Switching Scenarios

#### Hierarchical Navigation
```
Root → Client "acme-corp" → Site "building-a" → Gateway "gw-001" → Points
     → Client "beta-inc"  → Site "factory-x" → Points
```

#### Cross-Context Operations
```
# Working across multiple sites simultaneously
acme-corp/building-a> compare-with beta-inc/factory-x
acme-corp/building-a> copy-points-to beta-inc/factory-x --filter "hvac*"
```

### 1.4 Error Recovery Flows

#### Network Error Recovery
```
Connection lost → Show cached data → Retry with exponential backoff → 
Resume or work offline → Sync when reconnected
```

#### Authentication Error Recovery
```
Token expired → Prompt for re-auth → Save context → Restore session → Continue
```

#### Command Error Recovery
```
Invalid command → Show suggestions → Offer correction → Show help → Continue
```

## 2. Command Syntax Design

### 2.1 REPL-Specific Commands

#### Session Management
```bash
# Help system
help                    # Show general help
help <command>          # Show command-specific help
help <topic>           # Show topic help (clients, sites, points, etc.)

# Session control
exit                   # Exit REPL
quit                   # Exit REPL (alias)
clear                  # Clear screen
history                # Show command history
history <n>            # Show last n commands
!<n>                   # Execute command n from history
!!                     # Execute last command

# Context management
pwd                    # Show current context path
context                # Show current context details
context save <name>    # Save current context
context load <name>    # Load saved context
context list           # List saved contexts
context clear          # Clear current context

# Session persistence
save session <name>    # Save current session
load session <name>    # Load saved session
sessions               # List saved sessions
```

#### Configuration Commands
```bash
# Configuration management
config show            # Show current configuration
config set <key> <value>  # Set configuration value
config get <key>       # Get configuration value
config reset           # Reset to defaults
config reload          # Reload from file

# Output formatting
output table           # Set table output format
output json            # Set JSON output format
output csv             # Set CSV output format
output pretty          # Set pretty-printed format

# Display preferences
pager on/off           # Enable/disable paging
color on/off           # Enable/disable colors
verbose on/off         # Enable/disable verbose output
```

### 2.2 Context Navigation Commands

#### Hierarchical Navigation
```bash
# Root level navigation
clients                # List all clients
client <name>          # Enter client context
cd client:<name>       # Alternative syntax

# Client context navigation
sites                  # List sites for current client
site <name>            # Enter site context
gateways               # List gateways for current client
gateway <name>         # Enter gateway context

# Site context navigation
points                 # List points for current site
point <name>           # Enter point context
gateways               # List gateways for current site
discovered             # List discovered points

# Universal navigation
cd ..                  # Go up one level
cd /                   # Go to root
cd client:acme/site:building-a  # Absolute path
back                   # Go to previous context
forward                # Go to next context (if available)

# Quick context switching
use client <name>      # Switch to client context
use site <name>        # Switch to site context
use gateway <name>     # Switch to gateway context
```

### 2.3 Data Query Commands

#### List Operations
```bash
# Context-aware listing
ls                     # List items in current context
ls -l                  # List with detailed information
ls -a                  # List including archived items
ls --filter <pattern>  # Filter results by pattern

# Specific listing commands
clients --page 2       # Paginated client listing
sites --client acme    # Sites for specific client
points --collect-only  # Only points with collection enabled
gateways --status online  # Filter by status
```

#### Data Retrieval
```bash
# Timeseries queries
timeseries <point> --start "2024-01-01" --end "2024-01-02"
ts <point> -s "1d ago" -e "now"  # Shortened syntax with relative time
batch-ts --file points.txt --start "1h ago"  # Batch timeseries

# Information retrieval
info                   # Show detailed info for current context
status                 # Show status information
describe <item>        # Describe specific item
inspect <item>         # Deep inspection of item

# Search operations
search <pattern>       # Search in current context
find <name>           # Find by name
grep <pattern>        # Text search in descriptions
```

### 2.4 Shortcuts and Aliases

#### Common Command Aliases
```bash
# Navigation shortcuts
c <name>     → client <name>
s <name>     → site <name>
g <name>     → gateway <name>
p <name>     → point <name>

# List shortcuts
l            → ls
ll           → ls -l
la           → ls -a

# Common operations
q            → quit
h            → help
?            → help
..           → cd ..
~            → cd /

# Data shortcuts
ts           → timeseries
desc         → describe
cfg          → config
stat         → status
```

#### Tab Completion Shortcuts
```bash
# Intelligent completion based on context
client<TAB>             # Shows available clients
acme-corp/site<TAB>     # Shows sites for acme-corp
ts building-a.<TAB>     # Shows points for building-a
```

## 3. Interactive Features Specification

### 3.1 Command Completion Behavior

#### Context-Aware Completion
```bash
# Client context completion
aceiot> client <TAB>
acme-corp    beta-inc    gamma-solutions

# Site context completion
acme-corp> site <TAB>
building-a   building-b   warehouse-1

# Point context completion
building-a> ts <TAB>
building-a.hvac.temp.zone1    building-a.hvac.temp.zone2
building-a.lighting.level.1   building-a.electrical.power.main
```

#### Command Parameter Completion
```bash
# Time parameter completion
ts building-a.temp <TAB>
--start    --end    --format    --resolution

# Filter completion
ls --filter <TAB>
hvac*    electrical*    lighting*    archived*

# Configuration completion
config set <TAB>
output_format    api_timeout    batch_size    cache_ttl
```

#### Smart Suggestions
```bash
# Fuzzy matching
aceiot> client acm<TAB>
Did you mean: acme-corp?

# Command suggestions
aceiot> lst
Command not found. Did you mean:
  ls     - List items in current context
  list   - Show detailed list
  last   - Show last operation
```

### 3.2 History Search and Navigation

#### History Features
```bash
# History search (Ctrl+R style)
(reverse-i-search): ts building
ts building-a.hvac.temp.zone1 --start "1h ago"

# History substitution
!ts                    # Last command starting with 'ts'
!?building?            # Last command containing 'building'
^zone1^zone2           # Replace 'zone1' with 'zone2' in last command

# History navigation
Ctrl+P / Up Arrow     # Previous command
Ctrl+N / Down Arrow   # Next command
Alt+< / Ctrl+A        # Beginning of history
Alt+> / Ctrl+E        # End of history
```

#### Session History
```bash
# Persistent history across sessions
history save          # Save current session history
history merge          # Merge with saved history
history clear          # Clear current session history

# History analysis
history stats          # Show usage statistics
history search <term>  # Search across all history
```

### 3.3 Multi-line Input Handling

#### Multi-line Commands
```bash
# Explicit multi-line (backslash continuation)
aceiot> batch-ts \
...     --file points.txt \
...     --start "2024-01-01" \
...     --end "2024-01-02" \
...     --format csv

# Block input mode (triple quotes)
aceiot> create-points """
... {
...   "name": "new.point.1",
...   "site": "building-a",
...   "type": "analog"
... }
... """
```

#### Interactive Data Entry
```bash
# Guided input for complex operations
aceiot> create-site
Site name: new-building
Client [current: acme-corp]: 
Address: 123 Main St
Latitude: 40.7128
Longitude: -74.0060
Confirm creation? [y/N]: y
```

### 3.4 Output Pagination and Formatting

#### Intelligent Paging
```bash
# Automatic paging for large outputs
aceiot> ls points
Showing 1-50 of 1,247 points
... [point list] ...
--More-- (space=next page, q=quit, h=help)

# Paging controls
Space / Enter         # Next page
b / Backspace        # Previous page
g                    # Go to first page
G                    # Go to last page
/<pattern>           # Search in output
q                    # Quit pager
```

#### Dynamic Formatting
```bash
# Auto-format based on terminal size
aceiot> ls clients
# Wide terminal - full table
ID    Name         Nice Name       Bus Contact    Tech Contact
123   acme-corp    ACME Corp      john@acme.com  tech@acme.com

# Narrow terminal - compact view
ID    Name         Contact
123   acme-corp    john@acme.com
```

#### Interactive Output
```bash
# Clickable/selectable output (where supported)
aceiot> ls sites
1. building-a    [Active]   123 Main St
2. building-b    [Archived] 456 Oak Ave
3. warehouse-1   [Active]   789 Pine Rd

Select site (1-3, or name): 2
# Automatically executes: site building-b
```

## 4. Visual Design

### 4.1 Prompt Design with Context Indicators

#### Basic Prompt Structure
```bash
# Root context
aceiot> 

# Client context
aceiot[acme-corp]> 

# Site context
aceiot[acme-corp/building-a]> 

# Gateway context
aceiot[acme-corp/gw-001]> 

# Point context
aceiot[acme-corp/building-a.hvac.temp.zone1]> 
```

#### Enhanced Prompt with Status
```bash
# With connection status
aceiot[●online]> 

# With context and status
aceiot[acme-corp/building-a ●online]> 

# Offline mode
aceiot[acme-corp/building-a ○offline]> 

# With operation count
aceiot[acme-corp/building-a ●online 15ops]> 
```

#### Color-Coded Prompts
```bash
# Green for normal operation
\033[32maceiot[acme-corp]\033[0m> 

# Yellow for warnings
\033[33maceiot[acme-corp ⚠cache-only]\033[0m> 

# Red for errors
\033[31maceiot[disconnected]\033[0m> 

# Blue for special modes
\033[34maceiot[debug-mode]\033[0m> 
```

### 4.2 Error Message Formatting

#### Structured Error Display
```
┌─ Error: API Request Failed ─────────────────────────────────────┐
│ ✗ Unable to fetch clients list                                 │
│                                                                 │
│ Details:                                                        │
│   • Status: 401 Unauthorized                                   │
│   • Message: Invalid API key                                   │
│   • Endpoint: /api/clients/                                     │
│                                                                 │
│ Suggestions:                                                    │
│   • Check your API key with: config show                       │
│   • Refresh credentials with: config set api_key <new-key>     │
│   • Test connection with: ping                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Progressive Error Information
```bash
# Level 1: Simple error
✗ Command failed: Invalid point name

# Level 2: With details (verbose mode)
✗ Command failed: Invalid point name
  Point 'building-a.hvac.invalid' not found
  
# Level 3: With suggestions
✗ Command failed: Invalid point name
  Point 'building-a.hvac.invalid' not found
  
  Did you mean:
    • building-a.hvac.temp.zone1
    • building-a.hvac.humidity.zone1
    
  Use 'search hvac' to find related points
```

### 4.3 Help System Layout

#### Contextual Help Display
```
┌─ Help: Client Context ──────────────────────────────────────────┐
│                                                                 │
│ Available Commands:                                             │
│   sites              List sites for current client             │
│   site <name>        Enter site context                        │
│   gateways          List gateways for current client           │
│   gateway <name>    Enter gateway context                      │
│   info              Show client details                        │
│   back              Return to root context                     │
│                                                                 │
│ Navigation:                                                     │
│   cd ..             Go up one level                            │
│   cd /              Go to root                                 │
│   ls                List items in current context              │
│                                                                 │
│ Examples:                                                       │
│   sites --archived  Show archived sites                       │
│   site building-a   Enter building-a site context             │
│                                                                 │
│ Type 'help <command>' for detailed command help                │
└─────────────────────────────────────────────────────────────────┘
```

#### Interactive Help Navigation
```bash
# Topic-based help
help topics            # List all help topics
help navigation        # Help on navigation commands
help timeseries        # Help on timeseries operations
help contexts          # Help on context management

# Command discovery
help --search filter   # Find commands containing 'filter'
help --by-context      # Show commands available in current context
```

### 4.4 Status Indicators and Feedback

#### Real-time Status Bar
```
Status: ●Online | Context: acme-corp/building-a | Cache: 15 items | API: 250ms
```

#### Operation Progress
```bash
# Progress indicators for long operations
Fetching timeseries data... [████████░░] 80% (4.2s)

# Batch operation progress
Processing 150 points in batches...
Batch 1/3: [██████████] 100% (50 points) ✓
Batch 2/3: [████████░░] 80% (40/50 points)
Batch 3/3: [░░░░░░░░░░] 0% (pending)
```

#### Success Feedback
```bash
✓ Successfully retrieved 1,247 data points
✓ Context switched to: acme-corp/building-a
✓ Configuration saved
✓ 15 points exported to timeseries.csv
```

## 5. User Scenarios

### 5.1 Developer Exploring Site Data

#### Scenario: New Team Member Discovery
```bash
# Starting exploration
aceiot> help getting-started
aceiot> clients
aceiot> client acme-corp
acme-corp> info
acme-corp> sites
acme-corp> site building-a
building-a> ls -l
building-a> points --filter "hvac*"
building-a> ts building-a.hvac.temp.zone1 --start "1d ago"
building-a> describe building-a.hvac.temp.zone1
building-a> export --format csv --file hvac_data.csv
```

#### Typical Interactions
```bash
# Quick exploration with tab completion
aceiot> client ac<TAB>
aceiot> client acme-corp
acme-corp> site bu<TAB>
acme-corp> site building-a
building-a> points | grep temperature
building-a> ts building-a.hvac.temp.zone1 -s "1h ago"
```

### 5.2 Operations Team Monitoring Gateways

#### Scenario: Daily Health Check
```bash
# Morning monitoring routine
aceiot> use client operations
operations> gateways --status all
operations> gateway critical-gw-001
critical-gw-001> status
critical-gw-001> agents
critical-gw-001> config show
critical-gw-001> logs --tail 50
critical-gw-001> alert-if "cpu_usage > 80"
```

#### Alert Configuration
```bash
# Setting up monitoring
operations> gateways --health-check
operations> watch "gateways --status down" --interval 30s
operations> notify-on "gateway_down" --email ops@company.com
```

### 5.3 Data Analyst Running Time Series Queries

#### Scenario: Performance Analysis
```bash
# Batch analysis workflow
aceiot> context load energy-analysis
building-a> points --filter "electrical.*power"
building-a> batch-ts --file power_points.txt --start "30d ago" --format csv
building-a> statistical-summary power_data.csv
building-a> compare-periods --baseline "30d ago:15d ago" --current "15d ago:now"
```

#### Advanced Analytics
```bash
# Complex queries
building-a> query "SELECT avg(value) FROM timeseries WHERE point LIKE 'hvac.%' GROUP BY hour"
building-a> correlate building-a.weather.temp building-a.hvac.energy.consumption
building-a> export --analysis --format json --include-metadata
```

### 5.4 System Administrator Managing Configurations

#### Scenario: Gateway Configuration Update
```bash
# Configuration management
aceiot> gateway production-gw-001
production-gw-001> config backup --name "pre-update-$(date)"
production-gw-001> config edit agent_settings.json
# Opens interactive editor
production-gw-001> config validate
production-gw-001> config deploy --dry-run
production-gw-001> config deploy --confirm
production-gw-001> status --watch 60s
```

#### Bulk Operations
```bash
# Mass configuration updates
aceiot> gateways --filter "building-*"
aceiot> batch-config --update "logging.level=INFO" --target selected
aceiot> batch-config --restart --confirm --target selected
aceiot> monitor-deployment --timeout 300s
```

## 6. Accessibility Considerations

### 6.1 Screen Reader Support

#### Structured Content
```bash
# Semantic markup for screen readers
aceiot> ls --accessible
Region: Client List
  Heading Level 2: Available Clients
  Table: 3 columns, 5 rows
    Column Headers: Name, Status, Last Updated
    Row 1: acme-corp, Active, 2024-01-15
    Row 2: beta-inc, Active, 2024-01-14
```

#### Audio Feedback
```bash
# Optional audio cues
config set audio_feedback on
config set audio_voice "system_default"
config set audio_events "errors,success,navigation"
```

### 6.2 Keyboard Navigation

#### Full Keyboard Access
```bash
# All operations accessible via keyboard
Tab                    # Move to next interactive element
Shift+Tab             # Move to previous interactive element
Enter                 # Activate current element
Escape                # Cancel current operation
```

#### Navigation Shortcuts
```bash
Ctrl+L                # Clear screen
Ctrl+C                # Interrupt current operation
Ctrl+D                # Exit REPL
Ctrl+R                # Reverse history search
Ctrl+A/E              # Beginning/end of line
```

### 6.3 High Contrast Mode

#### Color-blind Friendly
```bash
config set color_scheme high_contrast
config set color_scheme deuteranopia_friendly
config set color_scheme protanopia_friendly
config set use_symbols_only true  # Use symbols instead of colors
```

## 7. Power-User Features

### 7.1 Scripting Integration

#### Command Chaining
```bash
# Pipe-like operations
aceiot> clients | filter active | sites | count
aceiot> gateways --status down | notify ops@company.com
aceiot> points --site building-a | timeseries --batch --start "1d ago" | export csv
```

#### Macro Recording
```bash
# Record and replay command sequences
macro record daily_check
aceiot> gateways --health
aceiot> sites --status
aceiot> alerts --active
macro stop

# Replay macro
macro play daily_check

# Schedule macro
macro schedule daily_check --cron "0 8 * * MON-FRI"
```

### 7.2 Advanced Filtering

#### Expression-based Filtering
```bash
# Complex filter expressions
points --where "type=='analog' AND collect_enabled==true AND site.contains('building')"
timeseries --filter "value > avg(value) * 1.2" --highlight-anomalies
gateways --expr "last_seen < '1h ago' OR cpu_usage > 80"
```

### 7.3 Custom Commands

#### Plugin System
```bash
# Load custom commands
plugin load ~/.aceiot/plugins/energy_analysis.py
plugin list
plugin help energy_analysis

# Use custom command
building-a> energy-analysis --period "last_month" --baseline "previous_month"
```

#### Command Aliases
```bash
# Define custom aliases
alias morning_check "gateways --health && sites --status && alerts --active"
alias energy_report "points --filter energy | timeseries --period 1d | export csv"

# Use aliases
aceiot> morning_check
building-a> energy_report --filename "energy_$(date +%Y%m%d).csv"
```

### 7.4 Data Export and Integration

#### Multiple Export Formats
```bash
# Export options
export --format csv --file data.csv
export --format json --file data.json --pretty
export --format parquet --file data.parquet --compress
export --format excel --file report.xlsx --include-charts
```

#### Integration Hooks
```bash
# External system integration
export --to-influxdb --database production_metrics
export --to-s3 --bucket analytics-data --key "hourly/$(date +%Y/%m/%d/%H).csv"
export --webhook https://analytics.company.com/api/data --format json
```

---

This specification provides a comprehensive framework for implementing a powerful, user-friendly REPL mode that caters to different user types while maintaining consistency with the existing CLI architecture. The design emphasizes discoverability, efficiency, and accessibility while providing advanced features for power users.