import pandas as pd

from .config import RAW_PATH, SIZE_THRESHOLD_MB, CHUNK_SIZE
from .utils import memory_mb, read_csv_smart


def build_profiling(df):
    nulls = df.isna().sum()
    null_pct = (nulls / len(df) * 100).round(2) if len(df) else nulls
    cardinality = df.nunique(dropna=True)
    duplicates = int(df.duplicated().sum())

    profile_df = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "nulls": nulls,
            "null_pct": null_pct,
            "nunique": cardinality,
        }
    )

    metrics = {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "duplicates": duplicates,
        "memory_mb": round(memory_mb(df), 2),
    }

    return {
        "profile_df": profile_df,
        "metrics": metrics,
        "nulls": nulls,
        "null_pct": null_pct,
        "cardinality": cardinality,
        "duplicates": duplicates,
    }


def extract_raw(
    path=RAW_PATH,
    size_threshold_mb=SIZE_THRESHOLD_MB,
    chunk_size=CHUNK_SIZE,
    logger=None,
):
    df = read_csv_smart(
        path,
        size_threshold_mb=size_threshold_mb,
        chunk_size=chunk_size,
        logger=logger,
    )
    profiling = build_profiling(df)
    return df, profiling
