from __future__ import annotations

import os
from pathlib import Path


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "Next-Gen-IT Audit API")
        self.app_env = os.getenv("APP_ENV", "development")
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv(
                "APP_CORS_ORIGINS",
                "http://localhost:4173,http://127.0.0.1:4173",
            ).split(",")
            if origin.strip()
        ]
        self.data_dir = Path(os.getenv("DATA_DIR", "./data")).resolve()
        self.report_dir = Path(os.getenv("REPORT_DIR", str(self.data_dir / "reports"))).resolve()
        self.upload_dir = Path(os.getenv("UPLOAD_DIR", str(self.data_dir / "uploads"))).resolve()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
