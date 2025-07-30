import logging

import aiohttp

from .models import (
    AnalysisServerResponse,
    Issue,
    ScanPathResult,
    VerifyServerRequest,
)

logger = logging.getLogger(__name__)


POLICY_PATH = "src/mcp_scan/policy.gr"


async def analyze_scan_path(scan_path: ScanPathResult, base_url: str) -> ScanPathResult:
    url = base_url[:-1] if base_url.endswith("/") else base_url
    url = url + "/api/v1/public/mcp-analysis"
    headers = {"Content-Type": "application/json"}
    payload = VerifyServerRequest(root=[server.signature for server in scan_path.servers])

    # Server signatures do not contain any information about the user setup. Only about the server itself.
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload.model_dump_json()) as response:
                if response.status == 200:
                    results = AnalysisServerResponse.model_validate_json(await response.read())
                else:
                    raise Exception(f"Error: {response.status} - {await response.text()}")

        scan_path.issues += results.issues

    except Exception as e:
        try:
            errstr = str(e.args[0])
            errstr = errstr.splitlines()[0]
        except Exception:
            errstr = ""
        for server_idx, server in enumerate(scan_path.servers):
            if server.signature is not None:
                for i, _ in enumerate(server.entities):
                    scan_path.issues.append(
                        Issue(
                            code="X001",
                            message=f"could not reach analysis server {errstr}",
                            reference=(server_idx, i),
                        )
                    )
    return scan_path
