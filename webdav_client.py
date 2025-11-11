
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from pathlib import Path
import os

from config import WEBDAV_BASE, WEBDAV_HOST, WEBDAV_FOLDER, WEBDAV_TOKEN, WEBDAV_PASS

_session = requests.Session()
_session.auth = (WEBDAV_TOKEN, WEBDAV_PASS)

def _propfind(url: str, depth: str = "1") -> str:
    r = _session.request("PROPFIND", url, headers={"Depth": depth})
    r.raise_for_status()
    return r.text

def list_remote_txts():
    """
    Recursive listing under WEBDAV_FOLDER.
    Returns: [{"name","href","etag","mtime","size"}]
    """
    url = urljoin(WEBDAV_BASE, WEBDAV_FOLDER)
    xml = _propfind(url, depth="infinity")
    ns = {"d": "DAV:"}
    root = ET.fromstring(xml)
    items = []
    for resp in root.findall("d:response", ns):
        href_el = resp.find("d:href", ns)
        if href_el is None:
            continue
        href = (href_el.text or "").strip()
        if not href.lower().endswith(".txt"):
            continue

        propstat = resp.find("d:propstat", ns)
        if propstat is None:
            continue
        props = propstat.find("d:prop", ns)
        if props is None:
            continue

        name = props.findtext("d:displayname", default=href.split("/")[-1], namespaces=ns)
        if not name or not name.lower().endswith(".txt"):
            continue

        etag = (props.findtext("d:getetag", default="", namespaces=ns) or "").strip('"')
        mtime = props.findtext("d:getlastmodified", default="", namespaces=ns) or ""
        size_text = props.findtext("d:getcontentlength", default="0", namespaces=ns) or "0"
        try:
            size = int(size_text)
        except Exception:
            size = 0

        file_url = urljoin(WEBDAV_HOST, href)
        items.append({"name": name, "href": file_url, "etag": etag, "mtime": mtime, "size": size})
    return sorted(items, key=lambda x: (x["name"].lower(), x["href"]))

def remote_snapshot_hash(items) -> str:
    """Hash of folder state to drive cache invalidation."""
    import hashlib
    s = "\n".join(f'{it["name"]}|{it["href"]}|{it["etag"]}|{it["mtime"]}|{it["size"]}' for it in items)
    return hashlib.sha256(s.encode()).hexdigest()

class RemoteTxt(os.PathLike):
    """Path-like wrapper for a remote text file so code can call .read_text(), .stem."""
    def __init__(self, name: str, href: str, etag: str = "", mtime: str = "", size: int = 0):
        self.name = name
        self.href = href
        self.etag = etag
        self.mtime = mtime
        self.size = size

    def read_text(self, encoding="utf-8", errors="ignore") -> str:
        r = _session.get(self.href)
        r.raise_for_status()
        r.encoding = r.encoding or "utf-8"
        return r.text

    def __fspath__(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def stem(self):
        return Path(self.name).stem
