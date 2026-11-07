import os

def use_temporal() -> bool:
    return os.getenv("USE_TEMPORAL_INGESTION", "false").lower() in ["true", "1", "yes", "y"]