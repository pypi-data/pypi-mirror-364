import json
import logging
import sys
import time
from datetime import datetime, timezone

import click
import httpx
from yumako import env

log = logging.getLogger(__name__)

_record = None
_enabled = None
_version = None


def disable():
    global _enabled
    _enabled = False


def _is_disabled():
    global _enabled
    if _enabled is None:
        _enabled = env.bool("HCS_CLI_TELEMETRY", True)
    return not _enabled


def _get_version():
    global _version
    if _version is None:
        try:
            from importlib.metadata import version

            _version = version("hcs-cli")
        except Exception as e:
            log.debug(f"Failed to get hcs-cli version: {e}")
            _version = "unknown"
    return _version


def start(cmd_path: str, params: dict):
    if _is_disabled():
        return

    global _record
    _record = {
        "@timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "command": cmd_path,
        "options": [k.replace("_", "-") for k, v in params.items() if v],
        "return": -1,
        "error": None,
        "time_ms": -1,
        "version": _get_version(),
        "env": {
            "python_version": sys.version,
            "platform": sys.platform,
            "executable": sys.executable,
        },
    }


def end(return_code: int = 0, error: Exception = None):
    if _is_disabled():
        return

    if _record is None:
        return

    if error:
        if isinstance(error, click.exceptions.Exit):
            return_code = error.exit_code
        elif isinstance(error, SystemExit):
            return_code = error.code
        else:
            _record["error"] = str(error)
            if return_code == 0:
                return_code = 1
    _record["return"] = return_code
    _record["time_ms"] = int((time.time() - datetime.fromisoformat(_record["@timestamp"]).timestamp()) * 1000)

    # print('TELEMETRY end', json.dumps(_record, indent=4), flush=True)

    _injest(_record)
    return _record


def _injest(doc):
    try:
        response = httpx.post(
            f"https://collie.omnissa.com/es/hcs-cli/_doc",
            auth=("append_user", "public"),
            headers={"Content-Type": "application/json"},
            content=json.dumps(doc),
            timeout=4,
            verify=False,
        )
        response.raise_for_status()
    except Exception as e:
        log.debug(f"Telemetry ingestion failed: {e}", exc_info=True)
        return
