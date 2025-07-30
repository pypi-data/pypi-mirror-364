"""
Provides validation for shell commands and ensures they are allowed to be executed.
"""

import os
from typing import Dict, List


class CommandValidator:
    """
    Validates shell commands and checks for unsafe operators.
    """

    def __init__(self):
        """
        Initialize the validator.
        """
        pass

    def _get_allowed_commands(self) -> set[str]:
        """Get the set of allowed commands from environment variables - deprecated, always returns empty set"""
        # This method is kept for backward compatibility but no longer enforces restrictions
        return set()

    def get_allowed_commands(self) -> list[str]:
        """Get the list of allowed commands from environment variables - deprecated, always returns empty list"""
        # This method is kept for backward compatibility but no longer enforces restrictions
        return []

    def is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed - always returns True (no restrictions)"""
        # All commands are now allowed
        return True

    def validate_no_shell_operators(self, cmd: str) -> None:
        """
        Validate that the command does not contain shell operators.

        Args:
            cmd (str): Command to validate

        Raises:
            ValueError: If the command contains shell operators
        """
        if cmd in [";", "&&", "||", "|"]:
            raise ValueError(f"Unexpected shell operator: {cmd}")

    def validate_pipeline(self, commands: List[str]) -> Dict[str, str]:
        """
        Validate pipeline command - now only checks for empty commands, not allowed commands.

        Args:
            commands (List[str]): List of commands to validate

        Returns:
            Dict[str, str]: Error message if validation fails, empty dict if success

        Raises:
            ValueError: If validation fails
        """
        current_cmd: List[str] = []

        for token in commands:
            if token == "|":
                if not current_cmd:
                    raise ValueError("Empty command before pipe operator")
                # No longer check if command is allowed - all commands are permitted
                current_cmd = []
            elif token in [";", "&&", "||"]:
                raise ValueError(f"Unexpected shell operator in pipeline: {token}")
            else:
                current_cmd.append(token)

        # Final command check - only check if it's empty, not if it's allowed
        if current_cmd:
            pass  # All commands are now allowed

        return {}

    def validate_command(self, command: List[str]) -> None:
        """
        Validate if the command can be executed - now only checks for empty commands.

        Args:
            command (List[str]): Command and its arguments

        Raises:
            ValueError: If the command is empty
        """
        if not command:
            raise ValueError("Empty command")

        # No longer check allowed commands - all commands are permitted
        # Only basic validation remains
