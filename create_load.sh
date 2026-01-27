so#!/bin/bash
# Create CPU load for demo - uses your infinite loop trick!

DURATION=${1:-30}  # Default 30 seconds
CORES=$(nproc)

echo "=========================================="
echo "  CPU Load Generator for Demo"
echo "=========================================="
echo "Cores: $CORES"
echo "Duration: ${DURATION}s"
echo ""
echo "Creating load in 3 seconds..."
echo "Watch the agent terminal and dashboard!"
sleep 3

# Start background loops for each core
echo "Starting load..."
for i in $(seq 1 $CORES); do
    while true; do :; done &
    PIDS="$PIDS $!"
done

echo "✅ Load active on $CORES cores!"
echo "   PID list: $PIDS"
echo ""
echo "⏱️  Running for ${DURATION} seconds..."

# Wait for specified duration
sleep $DURATION

# Kill all the loops
echo ""
echo "🛑 Stopping load..."

# Try graceful kill first
if [ -n "$PIDS" ]; then
    kill $PIDS 2>/dev/null
    sleep 1
    
    # Check if any are still running, force kill if needed
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo "   Force killing stuck process $pid..."
            kill -9 $pid 2>/dev/null
        fi
    done
    
    echo "✅ Load stopped!"
else
    echo "⚠️  No processes to kill (load may not have started)"
fi

echo ""
echo "Check dashboard to see mode return to BALANCED"

