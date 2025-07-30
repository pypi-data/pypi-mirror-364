import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from e2b.sandbox.filesystem.filesystem import FileType
    from e2b.sandbox_sync.sandbox_api import SandboxQuery
    from e2b_code_interpreter import Sandbox
except ImportError:
    Sandbox = None

import time

from .base_env import BaseEnv


class E2BEnv(BaseEnv):
    """Environment backed by an E2B sandbox via `e2b-code-interpreter` SDK."""

    def __init__(
        self,
        base_path: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None,
        timeout: int = 3600,
        ports: Optional[List[int]] = [8080, 2664],
        sandbox: Optional["Sandbox"] = None,
    ):
        if Sandbox is None:
            raise ImportError(
                "e2b_code_interpreter is not installed. "
                "Please install it with `pip install panda-agi[e2b]`"
            )
        super().__init__(base_path, metadata)

        self.working_directory = self.base_path
        if sandbox:
            self.sandbox = sandbox
        else:
            self.sandbox = self._connect(timeout, metadata)

        self.timeout = timeout
        self.ports = ports

    def _connect(self, timeout: int, metadata: Optional[Dict[str, Any]] = None):
        if Sandbox is None:
            raise ImportError(
                "e2b_code_interpreter is not installed. "
                "Please install it with `pip install panda-agi[e2b]`"
            )
        sbx = Sandbox(metadata=metadata, timeout=timeout)
        # Ensure base directory exists within sandbox
        sbx.files.make_dir(str(self.base_path))
        return sbx

    @staticmethod
    def get_active_sandbox(metadata: Optional[Dict[str, Any]] = None):
        if Sandbox is None:
            raise ImportError(
                "e2b_code_interpreter is not installed. "
                "Please install it with `pip install panda-agi[e2b]`"
            )
        if metadata and "conversation_id" in metadata:
            query = SandboxQuery(metadata=metadata)
            matches = Sandbox.list(query=query)
            if not matches:
                raise Exception("Session destroyed, please restart the conversation")
            sbx_info = matches[0]
            sbx = Sandbox.connect(sbx_info.sandbox_id)
            sbx.set_timeout(
                1800
            )  # 30 minutes to keep instance alive after last request
            return sbx

        return None

    def change_directory(self, path: Union[str, Path]) -> Path:
        """
        Change the current working directory in the sandbox.

        Args:
            path: New working directory path (can be relative to base_path)

        Returns:
            The new working directory Path object (local abstraction),
            representing the directory in the sandbox.
        """
        # Resolve relative to current working_directory or absolute within base_path
        new_path = self._resolve_path(path)

        # Ensure it stays within base_path
        if not str(new_path).startswith(str(self.base_path)):
            new_path = self.base_path / Path(path)

        # In sandbox: ensure directory exists
        # E2B SDK: create directory (and parents) if needed
        # Use string path inside sandbox
        self.sandbox.files.make_dir(str(new_path))

        # Update local working_directory abstraction
        self.working_directory = new_path
        return self.working_directory

    async def exec_shell(
        self,
        command: str,
        timeout: Optional[float] = None,
        capture_output: bool = True,
        blocking: bool = True,
    ) -> Dict[str, Any]:
        """
        Runs a shell command inside the sandbox.
        """
        start = time.perf_counter()
        result = self.sandbox.commands.run(
            command, cwd=str(self.working_directory), timeout=timeout
        )
        end = time.perf_counter()

        return {
            "status": "success" if result.exit_code == 0 else "error",
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "return_code": result.exit_code,
            "execution_time": end - start,
        }

    async def write_file(
        self,
        path: Union[str, Path],
        content: Union[str, bytes],
        mode: str = "w",
        encoding: Optional[str] = "utf-8",
    ) -> Dict[str, Any]:
        """
        Writes a file into the sandbox filesystem.
        """
        resolved = self._resolve_path(path)
        entry = self.sandbox.files.write(str(resolved), content)

        # Replace base path prefix with "/" if it exists
        if entry.path.startswith(str(self.base_path)):
            entry.path = "/" + entry.path[len(str(self.base_path)) :].lstrip("/")

        return {"status": "success", "path": entry.path, "file": entry.name}

    async def read_file(
        self,
        path: Union[str, Path],
        mode: str = "r",
        encoding: Optional[str] = "utf-8",
    ) -> Dict[str, Any]:
        """
        Reads a file from the sandbox, optionally slicing lines.
        """
        resolved = self._resolve_path(path)
        format = "bytes" if "rb" in mode else "text"
        content = self.sandbox.files.read(str(resolved), format=format)

        if format == "bytes" and isinstance(content, bytearray):
            content = bytes(content)

        size = len(content) if isinstance(content, (bytes, str)) else 0
        return {
            "status": "success",
            "path": str(resolved),
            "size": size,
            "content": content,
        }

    async def delete_file(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Removes a file or directory in the sandbox.
        """
        resolved = self._resolve_path(path)
        self.sandbox.files.remove(str(resolved))
        return {"status": "success", "path": str(resolved)}

    async def list_files(
        self,
        path: Optional[Union[str, Path]] = None,
        recursive: bool = False,
        include_hidden: bool = False,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """
        Lists directory contents inside the sandbox.
        """
        try:
            resolved = self._resolve_path(path or self.current_directory)
            str_path = str(resolved)

            # Check if path exists
            try:
                self.sandbox.files.exists(str_path)
            except Exception:
                return {
                    "status": "error",
                    "message": f"Directory not found: {str_path}",
                    "path": str_path,
                }

            # Check if it's a directory by trying to list it
            try:
                depth = max_depth if recursive else 1  # set depth to 5 if recursive
                entries = self.sandbox.files.list(str_path, depth=depth)
            except Exception:
                # If listing fails, it might not be a directory
                return {
                    "status": "error",
                    "message": f"Path is not a directory: {str_path}",
                    "path": str_path,
                }

            files = []
            base_path = Path(str_path)

            for entry in entries:
                # Skip the directory itself
                if entry.path == str_path:
                    continue

                # Skip hidden files unless explicitly requested
                if not include_hidden and Path(entry.path).name.startswith("."):
                    continue

                # Get relative path from the base directory
                try:
                    rel_path = Path(entry.path).relative_to(base_path)
                except ValueError:
                    # If we can't get relative path, use the full path
                    rel_path = Path(entry.path)

                # Create file info dict similar to LocalEnv
                file_info = {
                    "name": Path(entry.path).name,
                    "path": entry.path,
                    "relative_path": str(rel_path),
                    "type": "directory" if entry.type == FileType.DIR else "file",
                }
                files.append(file_info)

            return {
                "status": "success",
                "path": str_path,
                "files": files,
                "total_files": len(files),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error listing files: {str(e)}",
                "path": str(resolved) if "resolved" in locals() else str(path),
            }

    async def path_exists(self, path: Union[str, Path]) -> bool:
        """
        Check if a path exists in the sandbox environment.

        Args:
            path: Path relative to current_directory or absolute within base_path.

        Returns:
            bool: True if the path exists, False otherwise
        """
        resolved = self._resolve_path(path)
        str_path = str(resolved)
        try:
            return self.sandbox.files.exists(str_path)
        except Exception:
            return False

    async def mkdir(
        self, path: Union[str, Path], parents: bool = False, exist_ok: bool = False
    ) -> Dict[str, Any]:
        """
        Create a directory in the sandbox environment.

        Args:
            path: Path relative to current_directory or absolute within base_path.
            parents: If True, create parent directories as needed.
            exist_ok: If False, an error is raised if the directory already exists.

        Returns:
            Dict[str, Any]: Result of the mkdir operation
        """
        resolved = self._resolve_path(path)
        str_path = str(resolved)

        try:
            # Check if directory already exists
            if exist_ok:
                try:
                    if self.sandbox.files.exists(str_path):
                        return {
                            "status": "success",
                            "path": str_path,
                            "message": "Directory already exists",
                        }
                except Exception:
                    # If checking existence fails, proceed with creation attempt
                    pass

            # Create parent directories if needed
            if parents:
                # Get all parent paths that need to be created
                parts = Path(str_path).parts
                current_path = "/"

                for i, part in enumerate(parts):
                    if i == 0 and part == "/":  # Skip root
                        continue

                    current_path = os.path.join(current_path, part)

                    # Skip creating the final directory (will be created below)
                    if i == len(parts) - 1:
                        continue

                    try:
                        # Try to create each parent directory, ignore if exists
                        try:
                            if not self.sandbox.files.exists(current_path):
                                self.sandbox.files.make_dir(current_path)
                        except Exception:
                            self.sandbox.files.make_dir(current_path)
                    except Exception:
                        # Continue if parent creation fails, the final mkdir will fail appropriately
                        pass

            # Create the actual directory
            self.sandbox.files.make_dir(str_path)
            return {"status": "success", "path": str_path}
        except Exception as e:
            if exist_ok:
                # Check if directory exists after failed creation attempt
                try:
                    if self.sandbox.files.exists(str_path):
                        return {
                            "status": "success",
                            "path": str_path,
                            "message": "Directory already exists",
                        }
                except Exception:
                    pass

            return {
                "status": "error",
                "message": f"Failed to create directory: {str_path}. Error: {str(e)}",
            }

    async def get_hosted_url(self, port) -> str:
        return self.sandbox.get_host(port)

    def kill(self):
        """
        Destructor: schedule sandbox.close() if possible.
        """
        self.sandbox.kill()

    async def is_port_available(self, port: int) -> bool:
        pass

    async def get_available_ports(self) -> List[int]:
        return self.ports
