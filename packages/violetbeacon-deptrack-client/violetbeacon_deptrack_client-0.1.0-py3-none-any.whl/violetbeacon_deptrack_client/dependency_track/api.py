"""
This file is part of Dependency-Track Client by VioletBeacon
Copyright (C) 2025  VioletBeacon, Limited.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import logging
from base64 import b64encode
from urllib.parse import urljoin
from dataclasses import dataclass

from requests import put

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60

@dataclass
class PutBomData:
    """Data class for put_bom"""
    base_url: str
    api_key: str
    project_name: str
    project_version: str
    autocreate: bool
    bom_filepath: str

def put_bom(data: PutBomData):
    """Upload a BOM to Dependency-Track.
    
    Example curl command:
    $ curl -X PUT https://{dependency-track-api-instance}/api/v1/bom -H \
        'Content-Type: application/json' -H 'X-Api-Key: {API-KEY}' \
        -d '{"autoCreate":true,"projectName":"{project_name}",\
        "projectVersion":"{project_version}","bom":"{base64(bom.json)}"}'
    """
    bom_bytes = b""
    try:
        with open(data.bom_filepath, "rb") as fh:
            bom_bytes = fh.read()
    except Exception as e:
        logger.fatal("bom not loaded from %s", data.bom_filepath)
        raise e

    bom = b64encode(bom_bytes).decode('utf-8')

    url = urljoin(data.base_url, "/api/v1/bom")
    logger.debug("sending PUT request to %s", url)

    req = put(
        url,
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": data.api_key
        },
        json={
            "autoCreate": data.autocreate,
            "projectName": data.project_name,
            "projectVersion": data.project_version,
            "bom": bom
        },
        timeout=DEFAULT_TIMEOUT
    )

    if not req.ok:
        raise RuntimeError(
            f"put_bom failed with status code {req.status_code}: {req.reason} ({req.content!r})")
