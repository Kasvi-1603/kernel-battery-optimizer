#!/bin/bash

echo "======================================"
echo "  AI Battery Saver - Setup Script"
echo "======================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "ERROR: This script should run on Ubuntu/Linux VM"
    echo "       Run master_server.py on Windows if needed"
    exit 1
fi

# Check if running with sudo for module operations
if [ "$EUID" -eq 0 ]; then 
    echo "NOTE: Running as root/sudo"
    SUDO_CMD=""
else
    SUDO_CMD="sudo"
fi

# Step 1: Check prerequisites
echo "[1/6] Checking prerequisites..."

if ! command -v gcc &> /dev/null; then
    echo "ERROR: gcc not found"
    echo "       Run: sudo apt install build-essential"
    exit 1
fi

if ! command -v make &> /dev/null; then
    echo "ERROR: make not found"
    echo "       Run: sudo apt install build-essential"
    exit 1
fi

if [ ! -d "/lib/modules/$(uname -r)/build" ]; then
    echo "ERROR: Kernel headers not found"
    echo "       Run: sudo apt install linux-headers-$(uname -r)"
    exit 1
fi

echo "      [OK] gcc, make, kernel headers found"
echo ""

# Step 2: Compile kernel module
echo "[2/6] Compiling kernel module..."

# Clean first
make clean &> /dev/null

if ! make; then
    echo "ERROR: Compilation failed"
    echo "       Install dependencies: sudo apt install build-essential linux-headers-$(uname -r)"
    exit 1
fi

echo "      [OK] Compilation successful"
echo ""

# Step 3: Unload old module if exists
echo "[3/6] Checking for existing module..."

if lsmod | grep -q ai_battery; then
    echo "      Found existing module, unloading..."
    $SUDO_CMD rmmod ai_battery_module 2>/dev/null
    sleep 1
fi

echo "      [OK] Ready to load new module"
echo ""

# Step 4: Load kernel module
echo "[4/6] Loading kernel module..."

if $SUDO_CMD insmod ai_battery_module.ko; then
    echo "      [OK] Module loaded successfully"
else
    echo "ERROR: Failed to load module"
    echo "       Check: sudo dmesg | tail -10"
    exit 1
fi
echo ""

# Step 5: Verify module
echo "[5/6] Verifying installation..."

sleep 1

if ! lsmod | grep -q ai_battery; then
    echo "ERROR: Module not found in lsmod"
    exit 1
fi

if [ ! -e /proc/ai_battery_stats ]; then
    echo "ERROR: /proc/ai_battery_stats not created"
    exit 1
fi

if [ ! -e /proc/ai_battery_control ]; then
    echo "ERROR: /proc/ai_battery_control not created"
    exit 1
fi

echo "      [OK] Module is active"
echo ""
echo "      === Current System Stats ==="
cat /proc/ai_battery_stats
echo "      ============================"
echo ""

# Step 6: Install Python dependencies
echo "[6/6] Installing Python dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    echo "       Run: sudo apt install python3"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "WARNING: pip3 not found"
    echo "         Run: sudo apt install python3-pip"
else
    echo "      Installing flask and requests..."
    pip3 install flask requests --quiet
    echo "      [OK] Python dependencies installed"
fi

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "Next Steps:"
echo ""
echo "  TERMINAL 1: Start master server"
echo "    $ python3 master_server.py"
echo ""
echo "  TERMINAL 2: Open dashboard"
echo "    $ firefox http://localhost:5000"
echo "    (or google-chrome http://localhost:5000)"
echo ""
echo "  TERMINAL 3: Run agent"
echo "    $ sudo python3 agent.py"
echo ""
echo "  OPTIONAL: Run demo"
echo "    $ python3 demo.py"
echo ""
echo "To unload module later:"
echo "  $ sudo rmmod ai_battery_module"
echo ""
echo "For detailed help, see: UBUNTU_SETUP.md"
echo ""

