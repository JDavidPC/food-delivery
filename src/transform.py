import numpy as np
import pandas as pd

from .utils import clean_text_columns, memory_mb, optimize_types, to_snake_case


def clean_data(df, logger=None):
    df_clean = df.copy()
    df_clean.columns = [to_snake_case(c) for c in df_clean.columns]

    rows_before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    rows_after = len(df_clean)

    num_cols = df_clean.select_dtypes(include=[np.number]).columns
    cat_cols = df_clean.select_dtypes(exclude=[np.number]).columns

    for col in num_cols:
        median_val = df_clean[col].median()
        df_clean[col] = df_clean[col].fillna(median_val)

    for col in cat_cols:
        mode_vals = df_clean[col].mode(dropna=True)
        fill_val = mode_vals.iloc[0] if not mode_vals.empty else "unknown"
        df_clean[col] = df_clean[col].fillna(fill_val)

    df_clean = clean_text_columns(df_clean)
    df_clean = optimize_types(df_clean)

    stats = {
        "rows_before": int(rows_before),
        "rows_after": int(rows_after),
        "memory_mb_before": round(memory_mb(df), 2),
        "memory_mb_after": round(memory_mb(df_clean), 2),
    }

    if logger is not None:
        logger.info("Rows before: %s, after dedup: %s", rows_before, rows_after)
        logger.info(
            "Memory MB raw: %.2f, cleaned: %.2f",
            stats["memory_mb_before"],
            stats["memory_mb_after"],
        )

    return df_clean, stats


def feature_engineering(df, logger=None):
    df_fe = df.copy()

    def ensure_column(name, default_value=np.nan):
        if name not in df_fe.columns:
            df_fe[name] = default_value

    ensure_column("delivery_time_minutes")
    ensure_column("order_value")
    ensure_column("traffic_level_score")
    ensure_column("weather_severity_score")
    ensure_column("customer_loyalty_score")
    ensure_column("discount_amount")
    ensure_column("tip_amount")
    ensure_column("final_amount_paid")
    ensure_column("order_hour")
    ensure_column("delayed_delivery_flag", 0)

    df_fe["delivery_time_category"] = pd.cut(
        df_fe["delivery_time_minutes"],
        bins=[-np.inf, 20, 40, 60, np.inf],
        labels=["fast", "normal", "slow", "very_slow"],
    )

    df_fe["order_value_category"] = pd.cut(
        df_fe["order_value"],
        bins=[-np.inf, 15, 30, 60, np.inf],
        labels=["low", "mid", "high", "premium"],
    )

    df_fe["high_traffic_flag"] = (df_fe["traffic_level_score"] >= 7).astype(int)
    df_fe["weather_risk_flag"] = (df_fe["weather_severity_score"] >= 7).astype(int)

    if df_fe["customer_loyalty_score"].notna().any():
        loyalty_bins = df_fe["customer_loyalty_score"].quantile([0.33, 0.66]).values
        df_fe["customer_loyalty_segment"] = pd.cut(
            df_fe["customer_loyalty_score"],
            bins=[-np.inf, loyalty_bins[0], loyalty_bins[1], np.inf],
            labels=["low", "mid", "high"],
        )
    else:
        df_fe["customer_loyalty_segment"] = "unknown"

    denom = df_fe["order_value"].replace(0, np.nan)
    df_fe["discount_percentage"] = (df_fe["discount_amount"] / denom) * 100
    df_fe["tip_percentage"] = (df_fe["tip_amount"] / denom) * 100

    denom_time = df_fe["delivery_time_minutes"].replace(0, np.nan)
    df_fe["cost_efficiency_score"] = df_fe["final_amount_paid"] / denom_time

    df_fe["peak_hour_flag"] = (
        df_fe["order_hour"].isin([11, 12, 13, 19, 20, 21]).astype(int)
    )

    traffic = df_fe["traffic_level_score"].fillna(0)
    weather = df_fe["weather_severity_score"].fillna(0)
    delayed = df_fe["delayed_delivery_flag"].fillna(0)
    df_fe["operational_risk_score"] = (
        traffic * 0.4 + weather * 0.4 + delayed * 10 * 0.2
    )

    return df_fe


def handle_outliers_iqr(df, cols=None, logger=None):
    df_out = df.copy()
    numeric_cols = cols or df_out.select_dtypes(include=[np.number]).columns.tolist()

    def iqr_bounds(series):
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        return q1 - 1.5 * iqr, q3 + 1.5 * iqr

    report = []
    for col in numeric_cols:
        lower, upper = iqr_bounds(df_out[col])
        mask = (df_out[col] < lower) | (df_out[col] > upper)
        count = int(mask.sum())
        report.append(
            {
                "column": col,
                "outliers": count,
                "lower": float(lower),
                "upper": float(upper),
            }
        )
        if count > 0:
            df_out[col] = df_out[col].clip(lower, upper)

    if logger is not None:
        top = sorted(report, key=lambda x: x["outliers"], reverse=True)[:5]
        logger.info("Outlier report (top 5): %s", top)

    return df_out, report
