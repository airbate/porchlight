"""Point the app-under-test at hermetic storage before app.main is imported."""

import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="porchlight-test-")
os.environ.setdefault("DATABASE_PATH", os.path.join(_tmp, "test.db"))
os.environ.setdefault("SNAPSHOTS_DIR", os.path.join(_tmp, "snapshots"))
