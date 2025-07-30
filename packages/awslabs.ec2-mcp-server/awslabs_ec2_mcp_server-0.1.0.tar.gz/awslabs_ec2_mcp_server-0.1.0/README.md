# AWS EC2 MCP Server

A Model Context Protocol (MCP) server for managing AWS EC2 instances, AMIs, security groups, volumes, and related infrastructure.

## Overview

This server provides comprehensive EC2 management capabilities through the MCP protocol, allowing you to:

- **EC2 Instances**: Launch, terminate, start, stop, and reboot instances
- **Security Groups**: Create, modify, and delete security groups and rules
- **Key Pairs**: Create, import, and delete SSH key pairs
- **EBS Volumes**: Create, attach, detach, and delete volumes
- **EBS Snapshots**: Create and manage volume snapshots
- **AMIs**: Create custom AMIs from instances and manage their lifecycle
- **VPC Management**: Create and manage VPCs, subnets, and networking components

## Features

### Core Functionality
- Full EC2 instance lifecycle management
- Security group and network ACL management
- EBS volume and snapshot operations
- AMI creation and management
- VPC and subnet operations
- Key pair management for SSH access

### Security Features
- Input validation for all AWS resource IDs
- Permission-based access control
- Response sanitization to prevent sensitive data leakage
- Configurable write operation protection
- AWS credentials validation

### Operational Features
- Comprehensive error handling
- Detailed logging and monitoring
- Support for AWS profiles and regions
- Tag-based resource management
- Batch operations where applicable

## Installation

```bash
# Clone the repository
git clone https://github.com/awslabs/mcp.git
cd mcp/src/ec2-mcp-server

# Install dependencies
pip install -e .

# Or install from PyPI (when available)
pip install awslabs.ec2-mcp-server
```

## Configuration

### AWS Credentials

Configure your AWS credentials using one of these methods:

1. **AWS CLI**:
   ```bash
   aws configure
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```

3. **IAM Roles** (recommended for EC2 instances)

### Environment Variables

- `AWS_REGION`: AWS region (default: us-east-1)
- `AWS_PROFILE`: AWS profile name (optional)
- `ALLOW_WRITE`: Enable write operations (default: false)
- `ALLOW_SENSITIVE_DATA`: Enable access to sensitive data (default: false)
- `FASTMCP_LOG_LEVEL`: Log level (default: INFO)
- `FASTMCP_LOG_FILE`: Log file path (optional)

### Security Settings

For security, write operations are disabled by default. To enable:

```bash
export ALLOW_WRITE=true
export ALLOW_SENSITIVE_DATA=true
```

## Usage

### Starting the Server

```bash
# Start the MCP server
ec2-mcp-server
```

### Available Tools

#### Instance Management
- `list_instances`: List EC2 instances with optional filtering
- `get_instance_details`: Get detailed information about a specific instance
- `launch_instance`: Launch new EC2 instances
- `terminate_instance`: Terminate running instances
- `start_instance`: Start stopped instances
- `stop_instance`: Stop running instances
- `reboot_instance`: Reboot instances

#### Security Groups
- `list_security_groups`: List security groups
- `get_security_group_details`: Get detailed security group information
- `create_security_group`: Create new security groups
- `delete_security_group`: Delete security groups
- `modify_security_group_rules`: Add or remove security group rules

#### Key Pairs
- `list_key_pairs`: List SSH key pairs
- `create_key_pair`: Create new key pairs
- `delete_key_pair`: Delete key pairs

#### EBS Volumes
- `list_volumes`: List EBS volumes
- `create_volume`: Create new volumes
- `delete_volume`: Delete volumes
- `attach_volume`: Attach volumes to instances
- `detach_volume`: Detach volumes from instances

#### EBS Snapshots
- `list_snapshots`: List EBS snapshots
- `create_snapshot`: Create volume snapshots

#### AMIs
- `list_amis`: List Amazon Machine Images
- `create_image`: Create AMIs from instances
- `deregister_image`: Deregister AMIs

#### VPC Management
- `list_vpcs`: List VPCs
- `create_vpc`: Create new VPCs
- `delete_vpc`: Delete VPCs
- `list_subnets`: List subnets

## Examples

### Launch an Instance

```python
# Launch a new t2.micro instance
response = await launch_instance(
    ami_id="ami-12345678",
    instance_type="t2.micro",
    key_name="my-key-pair",
    security_group_ids=["sg-12345678"],
    tags={"Name": "MyInstance", "Environment": "Dev"}
)
```

### Create a Security Group

```python
# Create a new security group
response = await create_security_group(
    group_name="web-server-sg",
    description="Security group for web servers",
    vpc_id="vpc-12345678"
)

# Add HTTP rule
await modify_security_group_rules(
    group_id=response["group_id"],
    action="add",
    rule_type="inbound",
    ip_protocol="tcp",
    from_port=80,
    to_port=80,
    cidr_blocks=["0.0.0.0/0"]
)
```

### Create and Attach an EBS Volume

```python
# Create a new volume
volume_response = await create_volume(
    availability_zone="us-east-1a",
    size=20,
    volume_type="gp3"
)

# Attach to an instance
await attach_volume(
    volume_id=volume_response["volume_id"],
    instance_id="i-12345678",
    device="/dev/sdf"
)
```

## Required AWS Permissions

The server requires the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

For production use, consider implementing more restrictive permissions based on your specific needs.

## Error Handling

The server provides comprehensive error handling for common scenarios:

- **Authentication Errors**: Invalid or missing AWS credentials
- **Permission Errors**: Insufficient AWS permissions
- **Resource Not Found**: When specified resources don't exist
- **Validation Errors**: Invalid input parameters or resource IDs
- **Rate Limiting**: AWS API rate limit exceeded

## Logging

The server uses Python's logging module. Configure logging level:

```bash
export FASTMCP_LOG_LEVEL=DEBUG
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=awslabs.ec2_mcp_server tests/
```

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Mypy**: Type checking
- **Ruff**: Linting

```bash
# Format code
black awslabs/
isort awslabs/

# Type checking
mypy awslabs/

# Linting
ruff check awslabs/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/awslabs/mcp/issues
- Documentation: https://awslabs.github.io/mcp/servers/ec2-mcp-server/

## Changelog

### v0.1.0
- Initial release
- Basic EC2 instance management
- Security group operations
- EBS volume management
- AMI operations
- VPC management
- Key pair management