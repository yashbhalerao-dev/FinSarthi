from pathlib import Path


class LocalDocumentStorage:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, profile_id: str, filename: str, payload: bytes) -> str:
        folder = self.root / profile_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / filename
        path.write_bytes(payload)
        return str(path)

    def read(self, reference: str) -> bytes:
        return Path(reference).read_bytes()
