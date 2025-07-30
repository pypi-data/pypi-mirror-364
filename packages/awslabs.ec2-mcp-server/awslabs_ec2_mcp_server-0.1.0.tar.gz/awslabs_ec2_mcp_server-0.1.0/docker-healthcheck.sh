#!/bin/bash
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

# Basic health check for AWS EC2 MCP Server
# This script verifies that the server can be imported and basic functionality works

echo "Starting health check for AWS EC2 MCP Server..."

# Check if Python can import the main module
python3 -c "
import sys
try:
    import awslabs.ec2_mcp_server
    from awslabs.ec2_mcp_server.server import mcp
    print('✓ Successfully imported EC2 MCP Server')
except ImportError as e:
    print(f'✗ Failed to import EC2 MCP Server: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✗ Unexpected error: {e}')
    sys.exit(1)

# Check if we can access basic AWS credentials (without making API calls)
try:
    from awslabs.ec2_mcp_server.aws_client import get_ec2_client
    # This should not fail even without credentials, it just creates the client
    client = get_ec2_client()
    print('✓ AWS client creation successful')
except Exception as e:
    print(f'✗ AWS client creation failed: {e}')
    sys.exit(1)

print('✓ Health check passed')
"

echo "Health check completed successfully!"