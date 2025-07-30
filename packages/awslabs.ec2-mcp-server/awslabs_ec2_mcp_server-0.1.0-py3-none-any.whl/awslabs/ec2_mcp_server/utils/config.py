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

"""
Configuration utilities for the EC2 MCP Server.
"""

import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


def get_config() -> Dict[str, Any]:
    """
    Gets the configuration for the EC2 MCP Server.

    Returns:
        Dict containing configuration values
    """
    config = {
        "aws_region": os.environ.get("AWS_REGION", "us-east-1"),
        "aws_profile": os.environ.get("AWS_PROFILE", None),
        "log_level": os.environ.get("FASTMCP_LOG_LEVEL", "INFO"),
        "log_file": os.environ.get("FASTMCP_LOG_FILE"),
        # Security settings via environment variables
        "allow-write": os.environ.get("ALLOW_WRITE", "").lower() in ("true", "1", "yes"),
        "allow-sensitive-data": os.environ.get("ALLOW_SENSITIVE_DATA", "").lower()
        in ("true", "1", "yes"),
        
        # Key storage configuration
        "default_storage_method": os.environ.get("DEFAULT_STORAGE_METHOD", "parameter_store"),
        "auto_store_private_keys": os.environ.get("AUTO_STORE_PRIVATE_KEYS", "true").lower() in ("true", "1", "yes"),
        
        # Storage-specific configuration
        "s3_keypair_bucket": os.environ.get("S3_KEYPAIR_BUCKET"),
        "s3_keypair_prefix": os.environ.get("S3_KEYPAIR_PREFIX", "private-keys"),
        "parameter_store_prefix": os.environ.get("PARAMETER_STORE_PREFIX", "/ec2/keypairs"),
        "secrets_manager_prefix": os.environ.get("SECRETS_MANAGER_PREFIX", "ec2/keypairs"),
        "encryption_salt": os.environ.get("ENCRYPTION_SALT", "ec2-mcp-default-salt"),
    }
    

   

    logger.info(f"Loaded configuration: {os.environ}")
    return config