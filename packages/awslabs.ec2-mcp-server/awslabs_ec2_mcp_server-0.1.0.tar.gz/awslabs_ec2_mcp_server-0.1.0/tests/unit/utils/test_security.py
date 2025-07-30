"""
Unit tests for security utilities.
"""

import pytest

from awslabs.ec2_mcp_server.utils.security import (
    PERMISSION_WRITE,
    PERMISSION_SENSITIVE_DATA,
    PERMISSION_NONE,
    SecurityError,
    ValidationError,
    validate_instance_id,
    validate_security_group_id,
    validate_vpc_id,
    validate_subnet_id,
    validate_ami_id,
    validate_volume_id,
    validate_key_pair_name,
    check_permission,
    ResponseSanitizer,
)


class TestValidateInstanceId:
    """Tests for validate_instance_id function."""

    def test_valid_instance_ids(self):
        """Test that valid instance IDs pass validation."""
        valid_ids = [
            "i-1234567890abcdef0",
            "i-12345678",
            "i-abcdef0123456789",
            "i-0123456789abcdef0"
        ]

        for instance_id in valid_ids:
            assert validate_instance_id(instance_id) is True

    def test_invalid_instance_ids(self):
        """Test that invalid instance IDs fail validation."""
        invalid_ids = [
            "instance-12345678",  # Wrong prefix
            "i-",  # Too short
            "i-1234567",  # Too short
            "i-1234567890abcdef01",  # Too long
            "i-1234567G",  # Invalid character
            "i-GGGGGGGG",  # Invalid characters
            "12345678",  # No prefix
            "",  # Empty string
            "i-123 456",  # Contains space
        ]

        for instance_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_instance_id(instance_id)


class TestValidateSecurityGroupId:
    """Tests for validate_security_group_id function."""

    def test_valid_security_group_ids(self):
        """Test that valid security group IDs pass validation."""
        valid_ids = [
            "sg-1234567890abcdef0",
            "sg-12345678",
            "sg-abcdef0123456789",
            "sg-0123456789abcdef0"
        ]

        for sg_id in valid_ids:
            assert validate_security_group_id(sg_id) is True

    def test_invalid_security_group_ids(self):
        """Test that invalid security group IDs fail validation."""
        invalid_ids = [
            "secgroup-12345678",  # Wrong prefix
            "sg-",  # Too short
            "sg-1234567",  # Too short
            "sg-1234567890abcdef01",  # Too long
            "sg-1234567G",  # Invalid character
            "12345678",  # No prefix
            "",  # Empty string
        ]

        for sg_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_security_group_id(sg_id)


class TestValidateVpcId:
    """Tests for validate_vpc_id function."""

    def test_valid_vpc_ids(self):
        """Test that valid VPC IDs pass validation."""
        valid_ids = [
            "vpc-1234567890abcdef0",
            "vpc-12345678",
            "vpc-abcdef0123456789",
            "vpc-0123456789abcdef0"
        ]

        for vpc_id in valid_ids:
            assert validate_vpc_id(vpc_id) is True

    def test_invalid_vpc_ids(self):
        """Test that invalid VPC IDs fail validation."""
        invalid_ids = [
            "vpc-",  # Too short
            "vpc-1234567",  # Too short
            "vpc-1234567890abcdef01",  # Too long
            "vpc-1234567G",  # Invalid character
            "12345678",  # No prefix
            "",  # Empty string
        ]

        for vpc_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_vpc_id(vpc_id)


class TestValidateSubnetId:
    """Tests for validate_subnet_id function."""

    def test_valid_subnet_ids(self):
        """Test that valid subnet IDs pass validation."""
        valid_ids = [
            "subnet-1234567890abcdef0",
            "subnet-12345678",
            "subnet-abcdef0123456789",
            "subnet-0123456789abcdef0"
        ]

        for subnet_id in valid_ids:
            assert validate_subnet_id(subnet_id) is True

    def test_invalid_subnet_ids(self):
        """Test that invalid subnet IDs fail validation."""
        invalid_ids = [
            "subnet-",  # Too short
            "subnet-1234567",  # Too short
            "subnet-1234567890abcdef01",  # Too long
            "subnet-1234567G",  # Invalid character
            "12345678",  # No prefix
            "",  # Empty string
        ]

        for subnet_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_subnet_id(subnet_id)


class TestValidateAmiId:
    """Tests for validate_ami_id function."""

    def test_valid_ami_ids(self):
        """Test that valid AMI IDs pass validation."""
        valid_ids = [
            "ami-1234567890abcdef0",
            "ami-12345678",
            "ami-abcdef0123456789",
            "ami-0123456789abcdef0"
        ]

        for ami_id in valid_ids:
            assert validate_ami_id(ami_id) is True

    def test_invalid_ami_ids(self):
        """Test that invalid AMI IDs fail validation."""
        invalid_ids = [
            "ami-",  # Too short
            "ami-1234567",  # Too short
            "ami-1234567890abcdef01",  # Too long
            "ami-1234567G",  # Invalid character
            "12345678",  # No prefix
            "",  # Empty string
        ]

        for ami_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_ami_id(ami_id)


class TestValidateVolumeId:
    """Tests for validate_volume_id function."""

    def test_valid_volume_ids(self):
        """Test that valid volume IDs pass validation."""
        valid_ids = [
            "vol-1234567890abcdef0",
            "vol-12345678",
            "vol-abcdef0123456789",
            "vol-0123456789abcdef0"
        ]

        for volume_id in valid_ids:
            assert validate_volume_id(volume_id) is True

    def test_invalid_volume_ids(self):
        """Test that invalid volume IDs fail validation."""
        invalid_ids = [
            "vol-",  # Too short
            "vol-1234567",  # Too short
            "vol-1234567890abcdef01",  # Too long
            "vol-1234567G",  # Invalid character
            "12345678",  # No prefix
            "",  # Empty string
        ]

        for volume_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_volume_id(volume_id)


class TestValidateKeyPairName:
    """Tests for validate_key_pair_name function."""

    def test_valid_key_pair_names(self):
        """Test that valid key pair names pass validation."""
        valid_names = [
            "my-key",
            "my_key",
            "mykey123",
            "test@example.com",
            "key with spaces",
            "key.with.dots",
            "key-with-dashes_and_underscores"
        ]

        for name in valid_names:
            assert validate_key_pair_name(name) is True

    def test_invalid_key_pair_names(self):
        """Test that invalid key pair names fail validation."""
        invalid_names = [
            "key$with$dollars",  # Invalid character
            "key#with#hash",  # Invalid character
            "key%with%percent",  # Invalid character
            "key&with&ampersand",  # Invalid character
            "key*with*asterisk",  # Invalid character
            "key(with)parens",  # Invalid character
            "key[with]brackets",  # Invalid character
            "key{with}braces",  # Invalid character
            "key|with|pipe",  # Invalid character
            "key\\with\\backslash",  # Invalid character
            "key/with/slash",  # Invalid character
            "key<with>angles",  # Invalid character
            "key?with?question",  # Invalid character
            "key=with=equals",  # Invalid character
            "key+with+plus",  # Invalid character
            "a" * 256,  # Too long
        ]

        for name in invalid_names:
            with pytest.raises(ValidationError):
                validate_key_pair_name(name)


class TestCheckPermission:
    """Tests for check_permission function."""

    def test_permission_write_enabled(self):
        """Test that write permission is allowed when enabled."""
        config = {"allow-write": True}
        assert check_permission(config, PERMISSION_WRITE) is True

    def test_permission_write_disabled(self):
        """Test that write permission is denied when disabled."""
        config = {"allow-write": False}
        with pytest.raises(SecurityError) as exc_info:
            check_permission(config, PERMISSION_WRITE)
        assert "Write operations are disabled" in str(exc_info.value)

    def test_permission_sensitive_data_enabled(self):
        """Test that sensitive data permission is allowed when enabled."""
        config = {"allow-sensitive-data": True}
        assert check_permission(config, PERMISSION_SENSITIVE_DATA) is True

    def test_permission_sensitive_data_disabled(self):
        """Test that sensitive data permission is denied when disabled."""
        config = {"allow-sensitive-data": False}
        with pytest.raises(SecurityError) as exc_info:
            check_permission(config, PERMISSION_SENSITIVE_DATA)
        assert "Access to sensitive data is not allowed" in str(exc_info.value)

    def test_permission_none_always_allowed(self):
        """Test that none permission is always allowed."""
        config = {"allow-write": False, "allow-sensitive-data": False}
        assert check_permission(config, PERMISSION_NONE) is True


class TestResponseSanitizer:
    """Tests for ResponseSanitizer class."""

    def test_sanitize_dict(self):
        """Test sanitization of dictionary responses."""
        response = {
            "status": "success",
            "instance_id": "i-12345678",
            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # 40 chars
            "password": "password=mysecret123",
            "ip_address": "192.168.1.100", 
            "email": "user@example.com",
            "nested": {
                "aws_access_key": "AKIAIOSFODNN7EXAMPLE",  # 20 chars
                "normal_field": "normal_value"
            }
        }

        sanitized = ResponseSanitizer.sanitize(response)

        # Check that normal fields are preserved
        assert sanitized["status"] == "success"
        assert sanitized["instance_id"] == "i-12345678"

        # Check that sensitive data is redacted
        assert "[REDACTED" in sanitized["secret_key"]
        assert "[REDACTED" in sanitized["password"]
        assert "[REDACTED" in sanitized["ip_address"]
        assert "[REDACTED" in sanitized["email"]
        assert "[REDACTED" in sanitized["nested"]["aws_access_key"]
        assert sanitized["nested"]["normal_field"] == "normal_value"

    def test_sanitize_list(self):
        """Test sanitization of list responses."""
        response = [
            {"instance_id": "i-12345678"},
            {"secret": "AKIAIOSFODNN7EXAMPLE"},
            "192.168.1.100"
        ]

        sanitized = ResponseSanitizer.sanitize(response)

        assert sanitized[0]["instance_id"] == "i-12345678"
        assert "[REDACTED" in sanitized[1]["secret"]
        assert "[REDACTED" in sanitized[2]

    def test_sanitize_string(self):
        """Test sanitization of string responses."""
        sensitive_string = "Access key: AKIAIOSFODNN7EXAMPLE, IP: 192.168.1.100"
        sanitized = ResponseSanitizer.sanitize(sensitive_string)
        
        assert "[REDACTED" in sanitized
        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
        assert "192.168.1.100" not in sanitized

    def test_add_security_warning(self):
        """Test adding security warnings for public resources."""
        response = {
            "status": "success",
            "public_ip": "54.123.45.67"
        }

        response_with_warning = ResponseSanitizer.add_security_warning(response)

        assert "warnings" in response_with_warning
        assert len(response_with_warning["warnings"]) > 0
        assert "public IP address" in response_with_warning["warnings"][0]

    def test_add_security_warning_no_public_ip(self):
        """Test that no warning is added when there's no public IP."""
        response = {
            "status": "success",
            "private_ip": "10.0.1.100"
        }

        response_with_warning = ResponseSanitizer.add_security_warning(response)

        assert "warnings" not in response_with_warning or len(response_with_warning.get("warnings", [])) == 0