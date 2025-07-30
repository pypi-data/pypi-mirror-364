#!/usr/bin/env python3
"""
Project analysis and context management for Agentix
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


class ProjectAnalyzer:
    """Analyzes project structure and maintains context"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        self.agent_md_path = self.project_dir / "agent.md"

    def crawl_project(self) -> dict:
        """Crawl project and gather comprehensive context"""
        context = {
            "project_path": str(self.project_dir),
            "timestamp": datetime.now().isoformat(),
            "git_status": self._get_git_status(),
            "file_structure": self._get_file_structure(),
            "key_files": self._analyze_key_files(),
            "dependencies": self._get_dependencies(),
            "agent_context": self._get_or_create_agent_context(),
        }
        return context

    def _get_git_status(self) -> dict:
        """Get git repository status"""
        if not (self.project_dir / ".git").exists():
            return {"is_git_repo": False}

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Get status with timeout to handle locks
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Get recent commits
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "is_git_repo": True,
                "current_branch": (
                    branch_result.stdout.strip()
                    if branch_result.returncode == 0
                    else "unknown"
                ),
                "status": (
                    status_result.stdout.strip()
                    if status_result.returncode == 0
                    else "unknown"
                ),
                "recent_commits": (
                    log_result.stdout.strip().split("\n")
                    if log_result.returncode == 0 and log_result.stdout.strip()
                    else []
                ),
                "has_changes": (
                    bool(status_result.stdout.strip())
                    if status_result.returncode == 0
                    else False
                ),
            }
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return {
                "is_git_repo": True,
                "error": f"Git access limited: {str(e)[:50]}...",
            }

    def _get_file_structure(self) -> dict:
        """Get project file structure"""
        structure = {}
        ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "dist",
            "build",
        }
        ignore_files = {".DS_Store", ".gitignore", "*.pyc", "*.pyo"}

        for root, dirs, files in os.walk(self.project_dir):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            rel_root = os.path.relpath(root, self.project_dir)
            if rel_root == ".":
                rel_root = ""

            structure[rel_root] = {
                "directories": dirs,
                "files": [
                    f
                    for f in files
                    if not any(f.endswith(ext.replace("*", "")) for ext in ignore_files)
                ],
            }

        return structure

    def _analyze_key_files(self) -> dict:
        """Analyze key project files for context"""
        key_files = {}

        # Common important files
        important_files = [
            "README.md",
            "readme.md",
            "README.txt",
            "package.json",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "Dockerfile",
            "docker-compose.yml",
            ".env.example",
            "config.yaml",
            "config.json",
        ]

        for filename in important_files:
            file_path = self.project_dir / filename
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    key_files[filename] = {
                        "size": len(content),
                        "content": (
                            content[:2000] if len(content) > 2000 else content
                        ),  # Truncate large files
                    }
                except Exception as e:
                    key_files[filename] = {"error": str(e)}

        return key_files

    def _get_dependencies(self) -> dict:
        """Extract project dependencies"""
        deps = {}

        # Python dependencies
        if (self.project_dir / "pyproject.toml").exists():
            deps["python"] = "pyproject.toml found"
        elif (self.project_dir / "requirements.txt").exists():
            try:
                req_content = (self.project_dir / "requirements.txt").read_text()
                deps["python"] = req_content.split("\n")[:10]  # First 10 deps
            except Exception:
                deps["python"] = "requirements.txt found but unreadable"

        # Node.js dependencies
        if (self.project_dir / "package.json").exists():
            try:
                pkg_content = (self.project_dir / "package.json").read_text()
                pkg_data = json.loads(pkg_content)
                deps["nodejs"] = {
                    "dependencies": list(pkg_data.get("dependencies", {}).keys())[:10],
                    "devDependencies": list(pkg_data.get("devDependencies", {}).keys())[
                        :10
                    ],
                }
            except Exception:
                deps["nodejs"] = "package.json found but unreadable"

        return deps

    def _get_or_create_agent_context(self) -> dict:
        """Get existing agent.md or create one"""
        if self.agent_md_path.exists():
            try:
                content = self.agent_md_path.read_text(encoding="utf-8")
                return {
                    "exists": True,
                    "content": content,
                    "last_modified": datetime.fromtimestamp(
                        self.agent_md_path.stat().st_mtime
                    ).isoformat(),
                }
            except Exception as e:
                return {"exists": True, "error": str(e)}
        else:
            # Create initial agent.md
            initial_content = self._create_initial_agent_md()
            try:
                self.agent_md_path.write_text(initial_content, encoding="utf-8")
                return {"exists": False, "created": True, "content": initial_content}
            except Exception as e:
                return {"exists": False, "error": str(e)}

    def _create_initial_agent_md(self) -> str:
        """Create initial agent.md content"""
        project_name = self.project_dir.name

        content = f"""# {project_name} - Agent Context

## Project Overview
This file maintains context for AI agents working on this project.

**Project Name**: {project_name}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Description
[Add a brief description of what this project does]

## Architecture Notes
[Document key architectural decisions and patterns]

## Development Guidelines
[Add coding standards, conventions, and best practices]

## Recent Changes
[Track significant changes and their reasoning]

## TODO / Known Issues
[List pending tasks and known problems]

## Agent Instructions
[Specific instructions for AI agents working on this project]

---
*This file is automatically managed by Agentix. Update it to provide better context for AI assistance.*
"""
        return content

    def update_agent_context(self, task: str, result: str) -> None:
        """Update agent.md with task completion info"""
        if not self.agent_md_path.exists():
            self._get_or_create_agent_context()

        try:
            current_content = self.agent_md_path.read_text(encoding="utf-8")

            # Update timestamp
            updated_content = current_content.replace(
                "**Last Updated**: ",
                f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )

            # Add to recent changes
            new_entry = f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M')} - {task}\n{result}\n"

            if "## Recent Changes" in updated_content:
                updated_content = updated_content.replace(
                    "## Recent Changes\n[Track significant changes and their reasoning]",
                    f"## Recent Changes\n[Track significant changes and their reasoning]{new_entry}",
                )
                updated_content = updated_content.replace(
                    "## Recent Changes\n", f"## Recent Changes{new_entry}\n"
                )

            self.agent_md_path.write_text(updated_content, encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not update agent.md: {e}")
