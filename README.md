# Kernel Battery Optimizer

AI-powered battery management system for Linux using kernel-level process scheduling optimization.

## Overview

This project implements an intelligent battery saver that dynamically adjusts process priorities based on system load using a weighted classification algorithm at the kernel level.

## Components

- **Kernel Module** (`ai_battery_module.c`) - Creates `/proc` interfaces for system monitoring and control
- **Master Server** (`master_server.py`) - Flask-based prediction server with web dashboard
- **Agent** (`agent.py`) - System monitoring daemon that communicates with kernel module
- **Dashboard** (`dashboard.html`) - Real-time web interface for monitoring and testing

## Quick Start

```bash
# Clone repository
git clone https://github.com/Kasvi-1603/kernel-battery-optimizer.git
cd kernel-battery-optimizer

# Run automated setup
chmod +x setup.sh
./setup.sh

# Start server
python3 master_server.py
```

Open browser: `http://localhost:5000`

## Requirements

- Ubuntu/Linux (kernel headers required)
- Python 3.x
- Flask, requests

## Installation

```bash
# Compile and load kernel module
make
sudo insmod ai_battery_module.ko

# Install Python dependencies
pip3 install -r requirements.txt

# Run agent (monitors system and applies predictions)
sudo python3 agent.py
```

## Power Modes

| Mode | Threshold | Nice Value | Description |
|------|-----------|------------|-------------|
| BALANCED | < 0.4 | 0 | Normal operation |
| MODERATE | 0.4-0.6 | 5 | Light throttling |
| POWER_SAVE | 0.6-0.8 | 10 | Aggressive power saving |
| CRITICAL | > 0.8 | 15 | Maximum battery preservation |

## Algorithm

```
stress_score = 0.6 × (CPU_usage/100) + 0.4 × (process_count/300)
```

Weighted linear classification with threshold-based decision boundaries.

## Testing

```bash
# Automated testing with 6 scenarios
python3 demo.py
```

## Architecture

```
Master Server (Flask) → Agent (Python) → Kernel Module (C) → Process Scheduler
```

## License

GPL (for kernel module compatibility)

