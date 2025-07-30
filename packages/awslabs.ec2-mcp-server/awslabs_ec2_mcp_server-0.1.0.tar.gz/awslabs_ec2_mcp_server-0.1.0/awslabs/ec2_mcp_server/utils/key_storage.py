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
Secure storage utility for EC2 key pair private keys.

SECURITY NOTE: This module only stores private keys securely in AWS services.
Private keys are NEVER retrieved through this interface for security reasons.
Users must access stored keys directly through AWS Console/CLI.
"""

import json
import logging
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
import base64
import hashlib

from awslabs.ec2_mcp_server.utils.aws import AWSClientManager, handle_aws_error

logger = logging.getLogger(__name__)


class KeyStorageManager:
    """
    Manages secure storage of EC2 key pair private keys using multiple storage backends.
    
    SECURITY DESIGN: This class only supports STORING private keys, not retrieving them.
    This prevents exposure of private keys to LLMs or unauthorized access through the MCP interface.
    To access stored keys, users must use AWS Console, CLI, or direct API calls with proper permissions.
    """
    
    STORAGE_METHODS = {
        "secrets_manager": "AWS Secrets Manager",
        "s3_encrypted": "Encrypted S3 Storage", 
        "parameter_store": "AWS Systems Manager Parameter Store"
    }
    
    def __init__(self, aws_client: AWSClientManager, config: Dict[str, Any]):
        """
        Initialize the key storage manager.
        
        Args:
            aws_client: AWS client manager instance
            config: Configuration dictionary
        """
        self.aws_client = aws_client
        self.config = config
        self.region = config.get("aws_region", "us-east-1")
        
    def _generate_encryption_key(self, key_name: str) -> bytes:
        """
        Generate a deterministic encryption key for S3 storage based on key name and config.
        
        Args:
            key_name: The EC2 key pair name
            
        Returns:
            32-byte encryption key
        """
        # Use a combination of key name and a secret salt for deterministic encryption
        salt = self.config.get("encryption_salt", "ec2-mcp-default-salt")
        combined = f"{key_name}:{salt}:{self.region}"
        hash_key = hashlib.sha256(combined.encode()).digest()
        return base64.urlsafe_b64encode(hash_key)
        
    async def store_private_key(
        self,
        key_name: str,
        private_key_material: str,
        storage_method: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Store private key using the specified storage method.
        
        Args:
            key_name: The EC2 key pair name
            private_key_material: The private key content
            storage_method: Storage method to use
            **kwargs: Additional method-specific parameters
            
        Returns:
            Dict containing storage results and metadata
        """
        try:
            if storage_method == "secrets_manager":
                return await self._store_in_secrets_manager(key_name, private_key_material, **kwargs)
            elif storage_method == "s3_encrypted":
                return await self._store_in_s3_encrypted(key_name, private_key_material, **kwargs)
            elif storage_method == "parameter_store":
                return await self._store_in_parameter_store(key_name, private_key_material, **kwargs)
            else:
                raise ValueError(f"Unsupported storage method: {storage_method}")
                
        except Exception as e:
            logger.error(f"Failed to store private key for {key_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to store private key: {str(e)}"
            }
    
    
    async def delete_stored_key(
        self,
        key_name: str,
        storage_method: str,
        storage_location: str
    ) -> Dict[str, Any]:
        """
        Delete stored private key.
        
        Args:
            key_name: The EC2 key pair name
            storage_method: Storage method used
            storage_location: Location identifier for the stored key
            
        Returns:
            Dict containing deletion results
        """
        try:
            if storage_method == "secrets_manager":
                return await self._delete_from_secrets_manager(storage_location)
            elif storage_method == "s3_encrypted":
                return await self._delete_from_s3_encrypted(storage_location)
            elif storage_method == "parameter_store":
                return await self._delete_from_parameter_store(storage_location)
            else:
                raise ValueError(f"Unsupported storage method: {storage_method}")
                
        except Exception as e:
            logger.error(f"Failed to delete stored key for {key_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to delete stored key: {str(e)}"
            }
    
    async def _store_in_secrets_manager(
        self,
        key_name: str,
        private_key_material: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Store private key in AWS Secrets Manager."""
        try:
            secrets_client = self.aws_client.get_client("secretsmanager")
            secret_name = f"ec2/keypairs/{key_name}"
            
            secret_value = {
                "private_key": private_key_material,
                "key_name": key_name,
                "created_by": "ec2-mcp-server"
            }
            
            create_params = {
                "Name": secret_name,
                "Description": description or f"Private key for EC2 key pair {key_name}",
                "SecretString": json.dumps(secret_value)
            }
            
            if tags:
                create_params["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]
            
            response = secrets_client.create_secret(**create_params)
            
            return {
                "status": "success",
                "storage_method": "secrets_manager",
                "storage_location": secret_name,
                "secret_arn": response["ARN"],
                "message": f"Private key stored in Secrets Manager: {secret_name}"
            }
            
        except Exception as e:
            logger.error(f"Secrets Manager storage failed: {e}")
            raise
    
    async def _store_in_s3_encrypted(
        self,
        key_name: str,
        private_key_material: str,
        bucket_name: Optional[str] = None,
        key_prefix: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store private key in S3 with client-side encryption."""
        try:
            s3_client = self.aws_client.get_client("s3")
            
            # Use configured bucket or default
            bucket = bucket_name or self.config.get("s3_keypair_bucket", f"ec2-mcp-keypairs-{self.region}")
            prefix = key_prefix or self.config.get("s3_keypair_prefix", "private-keys")
            s3_key = f"{prefix}/{key_name}.encrypted"
            
            # Encrypt the private key
            encryption_key = self._generate_encryption_key(key_name)
            fernet = Fernet(encryption_key)
            encrypted_data = fernet.encrypt(private_key_material.encode())
            
            # Store metadata alongside encrypted key
            metadata = {
                "key-name": key_name,
                "created-by": "ec2-mcp-server",
                "encryption-method": "fernet"
            }
            
            # Upload to S3 with server-side encryption
            s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=encrypted_data,
                ServerSideEncryption="AES256",
                Metadata=metadata,
                ContentType="application/octet-stream"
            )
            
            storage_location = f"s3://{bucket}/{s3_key}"
            
            return {
                "status": "success",
                "storage_method": "s3_encrypted",
                "storage_location": storage_location,
                "bucket": bucket,
                "key": s3_key,
                "message": f"Private key encrypted and stored in S3: {storage_location}"
            }
            
        except Exception as e:
            logger.error(f"S3 encrypted storage failed: {e}")
            raise
    
    async def _store_in_parameter_store(
        self,
        key_name: str,
        private_key_material: str,
        parameter_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Store private key in AWS Systems Manager Parameter Store."""
        try:
            ssm_client = self.aws_client.get_client("ssm")
            
            param_name = parameter_name or f"/ec2/keypairs/{key_name}/private-key"
            
            put_params = {
                "Name": param_name,
                "Value": private_key_material,
                "Type": "SecureString",
                "Description": description or f"Private key for EC2 key pair {key_name}",
                "Overwrite": False
            }
            
            if tags:
                put_params["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]
            
            ssm_client.put_parameter(**put_params)
            
            return {
                "status": "success",
                "storage_method": "parameter_store",
                "storage_location": param_name,
                "message": f"Private key stored in Parameter Store: {param_name}"
            }
            
        except Exception as e:
            logger.error(f"Parameter Store storage failed: {e}")
            raise
    
    
    async def _delete_from_secrets_manager(self, secret_name: str) -> Dict[str, Any]:
        """Delete secret from Secrets Manager."""
        try:
            secrets_client = self.aws_client.get_client("secretsmanager")
            secrets_client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
            
            return {
                "status": "success",
                "message": f"Secret deleted from Secrets Manager: {secret_name}"
            }
            
        except Exception as e:
            logger.error(f"Secrets Manager deletion failed: {e}")
            raise
    
    async def _delete_from_s3_encrypted(self, s3_location: str) -> Dict[str, Any]:
        """Delete encrypted key from S3."""
        try:
            s3_client = self.aws_client.get_client("s3")
            
            # Parse S3 location
            bucket, key = s3_location.replace("s3://", "").split("/", 1)
            
            s3_client.delete_object(Bucket=bucket, Key=key)
            
            return {
                "status": "success",
                "message": f"Encrypted key deleted from S3: {s3_location}"
            }
            
        except Exception as e:
            logger.error(f"S3 deletion failed: {e}")
            raise
    
    async def _delete_from_parameter_store(self, parameter_name: str) -> Dict[str, Any]:
        """Delete parameter from Parameter Store."""
        try:
            ssm_client = self.aws_client.get_client("ssm")
            ssm_client.delete_parameter(Name=parameter_name)
            
            return {
                "status": "success",
                "message": f"Parameter deleted from Parameter Store: {parameter_name}"
            }
            
        except Exception as e:
            logger.error(f"Parameter Store deletion failed: {e}")
            raise