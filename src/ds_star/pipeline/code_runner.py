import sys
import subprocess
import tempfile
from pathlib import Path

from ds_star.models.models import CodeRunnerResults


class CodeRunner:
    """Executes LLM-generated Python code in a subprocess and returns a standardized result."""

    def __init__(self, timeout_seconds: int = 600):
        self.timeout_seconds = timeout_seconds

    def run_code(self, code: str) -> CodeRunnerResults:
        """Execute code in a subprocess; capture stdout, stderr, and exit code; enforce timeout."""
        if not code or not code.strip():
            return CodeRunnerResults(
                code=code,
                output="",
                error="No code to run",
                success=False,
                timeout_exceeded=False,
                exit_code=None,
            )

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                [sys.executable, str(temp_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                encoding="utf-8",
                errors="replace",
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            return CodeRunnerResults(
                code=code,
                output=stdout,
                error=stderr if stderr else None,
                success=result.returncode == 0,
                timeout_exceeded=False,
                exit_code=result.returncode,
            )
        except subprocess.TimeoutExpired:
            return CodeRunnerResults(
                code=code,
                output="",
                error=f"Execution timed out after {self.timeout_seconds}s",
                success=False,
                timeout_exceeded=True,
                exit_code=None,
            )
        except Exception as e:
            return CodeRunnerResults(
                code=code,
                output="",
                error=str(e),
                success=False,
                timeout_exceeded=False,
                exit_code=None,
            )
        finally:
            temp_path.unlink(missing_ok=True)