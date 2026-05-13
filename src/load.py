import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

from .config import COLUMN_ALIASES
from .utils import ensure_columns, map_column


def build_star_schema(df, logger=None):
    df_dw = df.copy()

    for target, candidates in COLUMN_ALIASES.items():
        map_column(df_dw, target, candidates)

    date_col = None
    for c in ["order_datetime", "order_date", "order_timestamp"]:
        if c in df_dw.columns:
            date_col = c
            break
    if date_col is not None:
        dt = pd.to_datetime(df_dw[date_col], errors="coerce")
        if df_dw["order_hour"].isna().all():
            df_dw["order_hour"] = dt.dt.hour
        if df_dw["day_of_week"].isna().all():
            df_dw["day_of_week"] = dt.dt.day_name()
        if df_dw["month"].isna().all():
            df_dw["month"] = dt.dt.month

    ensure_columns(df_dw, ["customer_age", "premium_customer_flag", "customer_loyalty_score"])
    ensure_columns(
        df_dw,
        ["traffic_level_score", "weather_severity_score", "city_tier", "festival_or_weekend_flag"],
    )
    ensure_columns(df_dw, ["cancellation_flag", "delayed_delivery_flag", "refund_flag", "promo_code_used"])
    ensure_columns(
        df_dw,
        [
            "order_value",
            "delivery_fee",
            "discount_amount",
            "tip_amount",
            "final_amount_paid",
            "delivery_time_minutes",
            "preparation_time_minutes",
            "customer_rating",
        ],
    )

    denom_time = df_dw["delivery_time_minutes"].replace(0, np.nan)
    df_dw["delivery_efficiency_score"] = df_dw["final_amount_paid"] / denom_time

    dim_date = df_dw[["order_hour", "day_of_week", "month"]].drop_duplicates().reset_index(drop=True)
    dim_date["date_id"] = np.arange(1, len(dim_date) + 1)

    dim_customer_segment = df_dw[
        ["customer_age", "premium_customer_flag", "customer_loyalty_score"]
    ].drop_duplicates().reset_index(drop=True)
    dim_customer_segment["customer_segment_id"] = np.arange(1, len(dim_customer_segment) + 1)

    dim_delivery_conditions = df_dw[
        ["traffic_level_score", "weather_severity_score", "city_tier", "festival_or_weekend_flag"]
    ].drop_duplicates().reset_index(drop=True)
    dim_delivery_conditions["delivery_conditions_id"] = np.arange(1, len(dim_delivery_conditions) + 1)

    dim_order_status = df_dw[
        ["cancellation_flag", "delayed_delivery_flag", "refund_flag", "promo_code_used"]
    ].drop_duplicates().reset_index(drop=True)
    dim_order_status["order_status_id"] = np.arange(1, len(dim_order_status) + 1)

    fact = df_dw.merge(dim_date, on=["order_hour", "day_of_week", "month"], how="left")
    fact = fact.merge(
        dim_customer_segment,
        on=["customer_age", "premium_customer_flag", "customer_loyalty_score"],
        how="left",
    )
    fact = fact.merge(
        dim_delivery_conditions,
        on=["traffic_level_score", "weather_severity_score", "city_tier", "festival_or_weekend_flag"],
        how="left",
    )
    fact = fact.merge(
        dim_order_status,
        on=["cancellation_flag", "delayed_delivery_flag", "refund_flag", "promo_code_used"],
        how="left",
    )

    fact = fact[
        [
            "date_id",
            "customer_segment_id",
            "delivery_conditions_id",
            "order_status_id",
            "order_value",
            "delivery_fee",
            "discount_amount",
            "tip_amount",
            "final_amount_paid",
            "delivery_time_minutes",
            "preparation_time_minutes",
            "customer_rating",
            "delivery_efficiency_score",
        ]
    ]

    if logger is not None:
        logger.info("Star schema built: fact rows=%s", len(fact))

    dims = {
        "dim_date": dim_date,
        "dim_customer_segment": dim_customer_segment,
        "dim_delivery_conditions": dim_delivery_conditions,
        "dim_order_status": dim_order_status,
    }
    return dims, fact


def load_to_sqlite(dims, fact, dw_path, logger=None):
    engine = create_engine(f"sqlite:///{dw_path}")

    dims["dim_date"].to_sql("dim_date", engine, if_exists="replace", index=False)
    dims["dim_customer_segment"].to_sql(
        "dim_customer_segment", engine, if_exists="replace", index=False
    )
    dims["dim_delivery_conditions"].to_sql(
        "dim_delivery_conditions", engine, if_exists="replace", index=False
    )
    dims["dim_order_status"].to_sql(
        "dim_order_status", engine, if_exists="replace", index=False
    )
    fact.to_sql("fact_delivery_orders", engine, if_exists="replace", index=False)

    con = sqlite3.connect(dw_path)
    cur = con.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_delivery_orders(date_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_delivery_orders(customer_segment_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_conditions ON fact_delivery_orders(delivery_conditions_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_status ON fact_delivery_orders(order_status_id)")
    con.commit()
    con.close()

    if logger is not None:
        logger.info("Loaded SQLite DW at %s", dw_path)
