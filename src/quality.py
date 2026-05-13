import pandas as pd


def build_quality_report(df, profiling):
    row_count = len(df)
    nulls = profiling["nulls"]
    null_pct = profiling["null_pct"]
    cardinality = profiling["cardinality"]

    quality_df = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "nulls": nulls,
            "null_pct": null_pct,
            "nunique": cardinality,
        }
    )

    quality_df["high_cardinality"] = quality_df["nunique"] > (row_count * 0.5)
    quality_df["low_variance"] = quality_df["nunique"] <= 2
    quality_df["completeness"] = (1 - quality_df["null_pct"] / 100).round(3)

    metrics = {
        "total_rows": int(row_count),
        "total_columns": int(df.shape[1]),
        "duplicate_rows": int(profiling["duplicates"]),
        "avg_completeness": float(quality_df["completeness"].mean()),
        "high_cardinality_cols": int(quality_df["high_cardinality"].sum()),
        "low_variance_cols": int(quality_df["low_variance"].sum()),
    }

    return quality_df, metrics


def validate_data(df, fact=None):
    checks = []

    def add_check(name, condition):
        checks.append({"check": name, "status": "PASS" if condition else "FAIL"})

    if "order_id" in df.columns:
        add_check("order_id_not_null", df["order_id"].notna().all())
        add_check("order_id_unique", df["order_id"].is_unique)

    numeric_cols = [
        c
        for c in ["order_value", "final_amount_paid", "delivery_time_minutes"]
        if c in df.columns
    ]
    for col in numeric_cols:
        add_check(f"{col}_non_negative", (df[col] >= 0).all())

    if fact is not None:
        add_check("fact_rows_match", len(fact) == len(df))

    return checks


def assert_validations(checks):
    if not all(c["status"] == "PASS" for c in checks):
        failed = [c for c in checks if c["status"] != "PASS"]
        raise AssertionError(f"Validations failed: {failed}")
