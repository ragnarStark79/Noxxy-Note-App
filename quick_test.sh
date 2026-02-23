#!/bin/bash

echo "🧪 Testing Noxxy API..."
echo ""

# Test health endpoint
echo "1️⃣ Testing /health endpoint..."
curl -s http://localhost:5001/health
echo -e "\n"

# Test root endpoint
echo "2️⃣ Testing / endpoint..."
curl -s http://localhost:5001/
echo -e "\n"

# Create a note
echo "3️⃣ Creating a note..."
curl -s -X POST http://localhost:5001/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Note","content":"This is a test"}'
echo -e "\n"

# List notes
echo "4️⃣ Listing notes..."
curl -s http://localhost:5001/notes
echo -e "\n"

echo "✅ Tests completed!"

