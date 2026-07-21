"""
PowerShell subprocess helper.

Provides a single, centrally-logged entry point for running PowerShell
commands from the agent.  All collectors that need CIM/WMI data must use
this helper — never spawn their own subprocess calls.
"""

import subprocess

import structlog

logger = structlog.get_logger(__name__)

# PowerShell flags used for every invocation.
_PS_FLAGS: list[str] = [
    "powershell",
    "-NoProfile",
    "-NonInteractive",
    "-Command",
]

# Hard ceiling on how long a single PowerShell call may block.
_DEFAULT_TIMEOUT: int = 10


def run_powershell(command: str, timeout: int = _DEFAULT_TIMEOUT) -> str | None:
    """
    Execute a PowerShell command and return its stdout as a stripped string.

    Parameters
    ----------
    command:
        The PowerShell expression to execute (passed after ``-Command``).
    timeout:
        Seconds before the subprocess is killed and ``None`` is returned.
        Defaults to ``_DEFAULT_TIMEOUT`` (10 s).

    Returns
    -------
    str | None
        The stripped stdout of the command, or ``None`` on any failure
        (timeout, non-zero exit code, stderr output, OS error).

    Notes
    -----
    * ``-NoProfile`` and ``-NonInteractive`` prevent PowerShell from loading
      user profiles or prompting, keeping invocations fast and non-blocking.
    * Both stdout and stderr are captured; stderr is logged at DEBUG level
      for diagnostics without surfacing it to callers.
    * The function never raises — all exceptions result in ``None``.
    """
    log = logger.bind(command=command, timeout=timeout)
    log.debug("PowerShell execution started")

    try:
        result = subprocess.run(  # noqa: S603
            [*_PS_FLAGS, command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        log.warning("PowerShell command timed out")
        return None
    except FileNotFoundError:
        log.warning("PowerShell executable not found — is this a Windows host?")
        return None
    except OSError as exc:
        log.warning("PowerShell OS error", error=str(exc))
        return None

    if result.returncode != 0:
        log.debug(
            "PowerShell command exited with non-zero status",
            returncode=result.returncode,
            stderr=result.stderr.strip(),
        )
        return None

    if result.stderr.strip():
        log.debug("PowerShell stderr output", stderr=result.stderr.strip())

    stdout = result.stdout.strip()
    log.debug("PowerShell execution completed", stdout_length=len(stdout))
    return stdout or None
