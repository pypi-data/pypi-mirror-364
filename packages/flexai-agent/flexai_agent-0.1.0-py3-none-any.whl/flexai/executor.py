"""
Code execution engine with safety measures
"""

import logging
import os
import subprocess
import tempfile
import time
from typing import Any

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Safe code execution engine"""

    def __init__(self, timeout: int = 30):
        """Initialize code executor

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.supported_languages = {
            "python": {"extension": ".py", "command": ["python3"], "interpreter": True},
            "javascript": {
                "extension": ".js",
                "command": ["node"],
                "interpreter": True,
            },
            "bash": {"extension": ".sh", "command": ["bash"], "interpreter": True},
            "shell": {"extension": ".sh", "command": ["bash"], "interpreter": True},
        }

    def execute(self, code: str, language: str = "python") -> dict[str, Any]:
        """Execute code safely with timeout and sandboxing

        Args:
            code: Code to execute
            language: Programming language

        Returns:
            Dictionary with execution results
        """
        if language.lower() not in self.supported_languages:
            return {
                "success": False,
                "output": "",
                "error": f"Language '{language}' is not supported. Supported languages: {list(self.supported_languages.keys())}",
                "execution_time": 0,
            }

        lang_config = self.supported_languages[language.lower()]

        try:
            return self._execute_with_timeout(code, lang_config)
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
            }

    def _execute_with_timeout(
        self, code: str, lang_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute code with timeout protection

        Args:
            code: Code to execute
            lang_config: Language configuration

        Returns:
            Execution result dictionary
        """
        start_time = time.time()

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=lang_config["extension"], delete=False
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Prepare command
            command = lang_config["command"] + [temp_file]

            # Execute with timeout
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(temp_file),
                # Security: limit process capabilities
                preexec_fn=self._limit_process if os.name != "nt" else None,
            )

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                returncode = process.returncode
                execution_time = time.time() - start_time

                if returncode == 0:
                    return {
                        "success": True,
                        "output": stdout,
                        "error": stderr if stderr else "",
                        "execution_time": execution_time,
                    }
                else:
                    return {
                        "success": False,
                        "output": stdout,
                        "error": stderr or f"Process exited with code {returncode}",
                        "execution_time": execution_time,
                    }

            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return {
                    "success": False,
                    "output": "",
                    "error": f"Execution timed out after {self.timeout} seconds",
                    "execution_time": self.timeout,
                }

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def _limit_process(self):
        """Apply security limits to the process (Unix only)"""
        try:
            # Set process group to allow killing child processes
            os.setpgrp()

            # Apply resource limits if available
            try:
                import resource

                # Limit CPU time
                resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))

                # Limit memory usage (100MB)
                resource.setrlimit(
                    resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024)
                )

                # Limit number of processes
                resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))

            except ImportError:
                # Resource module not available
                pass

        except Exception as e:
            logger.warning(f"Could not apply process limits: {e}")

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported for execution

        Args:
            language: Programming language name

        Returns:
            True if supported, False otherwise
        """
        return language.lower() in self.supported_languages

    def get_supported_languages(self) -> list:
        """Get list of supported languages

        Returns:
            List of supported language names
        """
        return list(self.supported_languages.keys())

    def validate_code_safety(
        self, code: str, language: str = "python"
    ) -> dict[str, Any]:
        """Basic safety validation for code (simple heuristics)

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Validation result dictionary
        """
        warnings = []
        blocked = False

        # Define dangerous patterns (basic protection)
        dangerous_patterns = {
            "python": [
                "import os",
                "os.",
                "__import__",
                "exec(",
                "eval(",
                "subprocess",
                "system",
                "rm -rf",
                "del ",
                "rmdir",
                "open(",
                "file(",
                "socket",
                "urllib",
                "requests",
            ],
            "javascript": [
                "require('fs')",
                "require('child_process')",
                "require('os')",
                "eval(",
                "Function(",
                "process.exit",
                "require('http')",
                "require('https')",
                "require('net')",
            ],
            "bash": [
                "rm -rf",
                "rm -r",
                "dd if=",
                "mkfs",
                "fdisk",
                "wget",
                "curl",
                "nc ",
                "telnet",
                "ssh",
            ],
        }

        patterns = dangerous_patterns.get(language.lower(), [])

        for pattern in patterns:
            if pattern in code:
                if pattern in ["rm -rf", "del ", "rmdir", "dd if=", "mkfs"]:
                    blocked = True
                    warnings.append(
                        f"Potentially destructive operation detected: {pattern}"
                    )
                else:
                    warnings.append(f"Potentially risky operation detected: {pattern}")

        return {"safe": not blocked, "warnings": warnings, "blocked": blocked}
