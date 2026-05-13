import os
import re
import time

import numpy as np
import pandas as pd


class Timer:
    def __init__(self, name, timings=None, logger=None):
        self.name = name
        self.timings = timings if timings is not None else {}
        self.logger = logger

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start
        self.timings[self.name] = elapsed
        if self.logger is not None:
            self.logger.info("TIMER %s: %.4fs", self.name, elapsed)


def memory_mb(df):
    return df.memory_usage(deep=True).sum() / (1024 * 1024)


def detect_encoding(path, nbytes=100000):
    try:
        import chardet

        with open(path, "rb") as f:
            raw = f.read(nbytes)
        result = chardet.detect(raw)
        return result.get("encoding") or "utf-8"
    except Exception:
        return "utf-8"


def read_csv_smart(path, size_threshold_mb=100, chunk_size=200_000, logger=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

    size_bytes = os.path.getsize(path)
    if size_bytes == 0:
        raise ValueError("File is empty.")

    encoding = detect_encoding(path)
    if logger is not None:
        logger.info("Detected encoding: %s", encoding)

    size_mb = size_bytes / (1024 * 1024)
    if logger is not None:
        logger.info("File size MB: %.2f", size_mb)

    if size_mb > size_threshold_mb:
        chunks = []
        for chunk in pd.read_csv(
            path, encoding=encoding, chunksize=chunk_size, low_memory=False
        ):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
    else:
        df = pd.read_csv(path, encoding=encoding, low_memory=False)

    return df


def to_snake_case(name):
    name = re.sub(r"[^0-9a-zA-Z]+", "_", str(name))
    name = re.sub(r"__+", "_", name)
    return name.strip("_").lower()


def clean_text_columns(df):
    df_clean = df.copy()
    for col in df_clean.select_dtypes(include=["object"]).columns:
        df_clean[col] = (
            df_clean[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"\s+", " ", regex=True)
        )
    return df_clean


def optimize_types(df, cat_threshold=0.3):
    df_opt = df.copy()
    for col in df_opt.select_dtypes(include=["int", "float"]).columns:
        df_opt[col] = pd.to_numeric(df_opt[col], downcast="float")

    for col in df_opt.select_dtypes(include=["object"]).columns:
        nunique = df_opt[col].nunique(dropna=True)
        if len(df_opt) > 0 and (nunique / len(df_opt)) < cat_threshold:
            df_opt[col] = df_opt[col].astype("category")

    return df_opt


def ensure_columns(df, cols, default_value=np.nan):
    for col in cols:
        if col not in df.columns:
            df[col] = default_value


def map_column(df, target, candidates):
    if target in df.columns and df[target].notna().any():
        return

    for col in candidates:
        if col in df.columns:
            df[target] = df[col]
            return

    if target not in df.columns:
        df[target] = np.nan
