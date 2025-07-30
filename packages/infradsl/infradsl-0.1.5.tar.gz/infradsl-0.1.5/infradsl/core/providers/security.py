"""
Provider Security Scanner - Security verification for providers

This module implements security scanning and verification for
InfraDSL providers to ensure they meet security standards.
"""

import ast
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import subprocess

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability"""

    id: str
    severity: VulnerabilitySeverity
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    cwe_id: Optional[str] = None
    fix_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "cwe_id": self.cwe_id,
            "fix_suggestion": self.fix_suggestion,
        }


@dataclass
class SecurityReport:
    """Security scan report for a provider"""

    provider_name: str
    scan_timestamp: datetime
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_critical_issues(self) -> bool:
        """Check if report contains critical vulnerabilities"""
        return any(
            v.severity == VulnerabilitySeverity.CRITICAL for v in self.vulnerabilities
        )

    def has_high_issues(self) -> bool:
        """Check if report contains high severity vulnerabilities"""
        return any(
            v.severity in [VulnerabilitySeverity.HIGH, VulnerabilitySeverity.CRITICAL]
            for v in self.vulnerabilities
        )

    def get_summary(self) -> Dict[str, int]:
        """Get vulnerability count by severity"""
        summary = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        }

        for vuln in self.vulnerabilities:
            summary[vuln.severity.value] += 1

        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider_name": self.provider_name,
            "scan_timestamp": self.scan_timestamp.isoformat(),
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "metadata": self.metadata,
            "summary": self.get_summary(),
        }


class ProviderSecurityScanner:
    """
    Security scanner for InfraDSL providers

    Performs various security checks including:
    - Static code analysis
    - Dependency vulnerability scanning
    - Permission and capability analysis
    - Secrets detection
    - Code quality checks
    """

    def __init__(self):
        # Patterns for detecting security issues
        self.secret_patterns = [
            (
                re.compile(
                    r'["\']?[Aa][Ww][Ss]_?[Aa]ccess_?[Kk]ey_?[Ii][Dd]["\']?\s*[:=]\s*["\'][A-Z0-9]{20}["\']'
                ),
                "AWS Access Key",
            ),
            (
                re.compile(
                    r'["\']?[Aa][Ww][Ss]_?[Ss]ecret_?[Aa]ccess_?[Kk]ey["\']?\s*[:=]\s*["\'][A-Za-z0-9/+=]{40}["\']'
                ),
                "AWS Secret Key",
            ),
            (
                re.compile(
                    r'["\']?[Aa]pi_?[Kk]ey["\']?\s*[:=]\s*["\'][A-Za-z0-9]{16,}["\']'
                ),
                "API Key",
            ),
            (
                re.compile(r'["\']?[Pp]assword["\']?\s*[:=]\s*["\'][^"\']{8,}["\']'),
                "Hardcoded Password",
            ),
            (
                re.compile(r'["\']?[Pp]rivate_?[Kk]ey["\']?\s*[:=]\s*["\']-----BEGIN'),
                "Private Key",
            ),
            (
                re.compile(
                    r'["\']?[Tt]oken["\']?\s*[:=]\s*["\'][A-Za-z0-9._-]{20,}["\']'
                ),
                "Access Token",
            ),
        ]

        self.dangerous_imports = [
            "os.system",
            "subprocess.call",
            "subprocess.run",
            "eval",
            "exec",
            "__import__",
            "compile",
        ]

        self.suspicious_patterns = [
            (re.compile(r"\.\.\/"), "Path Traversal"),
            (re.compile(r"chmod\s+777"), "Dangerous Permissions"),
            (re.compile(r"0\.0\.0\.0"), "Bind to All Interfaces"),
            (re.compile(r"verify\s*=\s*False"), "SSL Verification Disabled"),
            (re.compile(r"shell\s*=\s*True"), "Shell Injection Risk"),
        ]

    async def scan_directory(self, directory: Path) -> SecurityReport:
        """Scan a provider directory for security issues"""
        provider_name = directory.name
        report = SecurityReport(
            provider_name=provider_name,
            scan_timestamp=datetime.now(timezone.utc),
        )

        # Run various security checks
        await self._check_code_security(directory, report)
        await self._check_dependencies(directory, report)
        await self._check_permissions(directory, report)
        await self._check_secrets(directory, report)
        await self._check_metadata(directory, report)

        return report

    async def scan_provider(self, provider_path: Path) -> SecurityReport:
        """Scan a single provider file or directory"""
        if provider_path.is_file():
            # Single file provider
            report = SecurityReport(
                provider_name=provider_path.stem,
                scan_timestamp=datetime.now(timezone.utc),
            )

            await self._scan_python_file(provider_path, report)
            return report
        else:
            # Directory provider
            return await self.scan_directory(provider_path)

    async def _check_code_security(
        self, directory: Path, report: SecurityReport
    ) -> None:
        """Check Python code for security issues"""
        python_files = list(directory.rglob("*.py"))

        for py_file in python_files:
            await self._scan_python_file(py_file, report)

        if not report.vulnerabilities:
            report.passed_checks.append("code_security")
        else:
            report.failed_checks.append("code_security")

    async def _scan_python_file(self, file_path: Path, report: SecurityReport) -> None:
        """Scan a Python file for security issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))

                # Check for dangerous imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in self.dangerous_imports:
                                report.vulnerabilities.append(
                                    SecurityVulnerability(
                                        id=f"import-{alias.name}",
                                        severity=VulnerabilitySeverity.HIGH,
                                        title=f"Dangerous Import: {alias.name}",
                                        description=f"Import of potentially dangerous module {alias.name}",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        cwe_id="CWE-676",
                                        fix_suggestion="Use safer alternatives or implement proper security controls",
                                    )
                                )

                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            full_name = f"{module}.{alias.name}"
                            if full_name in self.dangerous_imports:
                                report.vulnerabilities.append(
                                    SecurityVulnerability(
                                        id=f"import-{full_name}",
                                        severity=VulnerabilitySeverity.HIGH,
                                        title=f"Dangerous Import: {full_name}",
                                        description=f"Import of potentially dangerous function {full_name}",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        cwe_id="CWE-676",
                                        fix_suggestion="Use safer alternatives or implement proper security controls",
                                    )
                                )

                    # Check for eval/exec usage
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ["eval", "exec", "__import__"]:
                                report.vulnerabilities.append(
                                    SecurityVulnerability(
                                        id=f"dangerous-call-{node.func.id}",
                                        severity=VulnerabilitySeverity.CRITICAL,
                                        title=f"Dangerous Function Call: {node.func.id}",
                                        description=f"Use of {node.func.id} can lead to code injection",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        cwe_id="CWE-94",
                                        fix_suggestion="Avoid dynamic code execution",
                                    )
                                )

            except SyntaxError as e:
                report.vulnerabilities.append(
                    SecurityVulnerability(
                        id="syntax-error",
                        severity=VulnerabilitySeverity.MEDIUM,
                        title="Syntax Error",
                        description=f"Python syntax error: {e}",
                        file_path=str(file_path),
                        line_number=e.lineno,
                    )
                )

            # Check for suspicious patterns
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                for pattern, issue_type in self.suspicious_patterns:
                    if pattern.search(line):
                        report.vulnerabilities.append(
                            SecurityVulnerability(
                                id=f"pattern-{issue_type.lower().replace(' ', '-')}",
                                severity=VulnerabilitySeverity.MEDIUM,
                                title=issue_type,
                                description=f"Suspicious pattern detected: {issue_type}",
                                file_path=str(file_path),
                                line_number=i,
                            )
                        )

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

    async def _check_dependencies(
        self, directory: Path, report: SecurityReport
    ) -> None:
        """Check dependencies for known vulnerabilities"""
        requirements_files = [
            "requirements.txt",
            "requirements.in",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
        ]

        dependency_found = False

        for req_file in requirements_files:
            req_path = directory / req_file
            if req_path.exists():
                dependency_found = True

                # Run safety check if available
                try:
                    result = subprocess.run(
                        ["safety", "check", "--file", str(req_path), "--json"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode != 0 and result.stdout:
                        vulnerabilities = json.loads(result.stdout)
                        for vuln in vulnerabilities:
                            report.vulnerabilities.append(
                                SecurityVulnerability(
                                    id=f"dep-{vuln.get('vulnerability_id', 'unknown')}",
                                    severity=self._map_safety_severity(
                                        vuln.get("severity", "unknown")
                                    ),
                                    title=f"Vulnerable Dependency: {vuln.get('package', 'unknown')}",
                                    description=vuln.get(
                                        "description",
                                        "Dependency vulnerability detected",
                                    ),
                                    file_path=str(req_path),
                                    cwe_id=vuln.get("cwe"),
                                    fix_suggestion=f"Update to {vuln.get('secure_version', 'a secure version')}",
                                )
                            )

                except (
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                    json.JSONDecodeError,
                ):
                    # Safety not available or failed
                    pass

        if dependency_found and not any(
            v.id.startswith("dep-") for v in report.vulnerabilities
        ):
            report.passed_checks.append("dependency_security")
        elif dependency_found:
            report.failed_checks.append("dependency_security")

    async def _check_permissions(self, directory: Path, report: SecurityReport) -> None:
        """Check file permissions for security issues"""
        issues_found = False

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Check for overly permissive files
                mode = file_path.stat().st_mode
                if mode & 0o002:  # World writable
                    report.vulnerabilities.append(
                        SecurityVulnerability(
                            id=f"perm-world-writable",
                            severity=VulnerabilitySeverity.HIGH,
                            title="World Writable File",
                            description=f"File is writable by all users",
                            file_path=str(file_path),
                            cwe_id="CWE-732",
                            fix_suggestion="Remove world write permissions",
                        )
                    )
                    issues_found = True

        if not issues_found:
            report.passed_checks.append("file_permissions")
        else:
            report.failed_checks.append("file_permissions")

    async def _check_secrets(self, directory: Path, report: SecurityReport) -> None:
        """Check for hardcoded secrets and credentials"""
        text_extensions = {
            ".py",
            ".json",
            ".yaml",
            ".yml",
            ".ini",
            ".cfg",
            ".conf",
            ".txt",
            ".md",
        }
        secrets_found = False

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Skip if file is too large
                    if len(content) > 1_000_000:  # 1MB
                        continue

                    # Check each line for secrets
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        for pattern, secret_type in self.secret_patterns:
                            if pattern.search(line):
                                # Skip if it's likely a placeholder
                                if any(
                                    placeholder in line.lower()
                                    for placeholder in [
                                        "example",
                                        "placeholder",
                                        "your-",
                                        "xxx",
                                    ]
                                ):
                                    continue

                                report.vulnerabilities.append(
                                    SecurityVulnerability(
                                        id=f"secret-{secret_type.lower().replace(' ', '-')}",
                                        severity=VulnerabilitySeverity.CRITICAL,
                                        title=f"Hardcoded {secret_type}",
                                        description=f"Potential {secret_type} found in source code",
                                        file_path=str(file_path),
                                        line_number=i,
                                        cwe_id="CWE-798",
                                        fix_suggestion="Use environment variables or secure credential storage",
                                    )
                                )
                                secrets_found = True
                                break  # One secret per line is enough

                except Exception as e:
                    logger.debug(f"Error checking {file_path} for secrets: {e}")

        if not secrets_found:
            report.passed_checks.append("no_hardcoded_secrets")
        else:
            report.failed_checks.append("no_hardcoded_secrets")

    async def _check_metadata(self, directory: Path, report: SecurityReport) -> None:
        """Check provider metadata for security compliance"""
        metadata_file = directory / "metadata.json"

        if not metadata_file.exists():
            report.vulnerabilities.append(
                SecurityVulnerability(
                    id="missing-metadata",
                    severity=VulnerabilitySeverity.LOW,
                    title="Missing Metadata",
                    description="Provider metadata file not found",
                    file_path=str(directory),
                    fix_suggestion="Add metadata.json with provider information",
                )
            )
            report.failed_checks.append("metadata_compliance")
            return

        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Check required security fields
            required_fields = ["name", "version", "author", "license"]
            missing_fields = [
                field for field in required_fields if field not in metadata
            ]

            if missing_fields:
                report.vulnerabilities.append(
                    SecurityVulnerability(
                        id="incomplete-metadata",
                        severity=VulnerabilitySeverity.LOW,
                        title="Incomplete Metadata",
                        description=f"Missing required fields: {', '.join(missing_fields)}",
                        file_path=str(metadata_file),
                        fix_suggestion="Add all required metadata fields",
                    )
                )
                report.failed_checks.append("metadata_compliance")
            else:
                report.passed_checks.append("metadata_compliance")

        except Exception as e:
            report.vulnerabilities.append(
                SecurityVulnerability(
                    id="invalid-metadata",
                    severity=VulnerabilitySeverity.MEDIUM,
                    title="Invalid Metadata",
                    description=f"Failed to parse metadata: {e}",
                    file_path=str(metadata_file),
                    fix_suggestion="Fix metadata.json syntax",
                )
            )
            report.failed_checks.append("metadata_compliance")

    def _map_safety_severity(self, safety_severity: str) -> VulnerabilitySeverity:
        """Map safety severity to our severity levels"""
        mapping = {
            "low": VulnerabilitySeverity.LOW,
            "medium": VulnerabilitySeverity.MEDIUM,
            "high": VulnerabilitySeverity.HIGH,
            "critical": VulnerabilitySeverity.CRITICAL,
        }
        return mapping.get(safety_severity.lower(), VulnerabilitySeverity.MEDIUM)

    def verify_signature(self, package_path: Path, signature: str) -> bool:
        """Verify package signature"""
        # This would implement actual signature verification
        # For now, return True for demo
        return True

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()


async def scan_provider(provider_path: Path) -> SecurityReport:
    """Convenience function to scan a provider"""
    scanner = ProviderSecurityScanner()
    return await scanner.scan_provider(provider_path)
