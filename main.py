from src.config import DW_PATH, PROCESSED_DIR, RAW_PATH, STAGING_DIR, ensure_dirs
from src.extract import extract_raw
from src.load import build_star_schema, load_to_sqlite
from src.logger import setup_logger
from src.quality import assert_validations, build_quality_report, validate_data
from src.transform import clean_data, feature_engineering, handle_outliers_iqr
from src.utils import Timer


def main():
    ensure_dirs()
    logger = setup_logger("etl", log_file="logs/etl.log")
    timings = {}

    logger.info("ETL started")

    with Timer("extract", timings, logger=logger):
        df_raw, profiling = extract_raw(path=RAW_PATH, logger=logger)

    with Timer("quality", timings, logger=logger):
        quality_df, quality_metrics = build_quality_report(df_raw, profiling)
        quality_df.to_csv(STAGING_DIR / "quality_report.csv", index=True)

    with Timer("transform_clean", timings, logger=logger):
        df_clean, clean_stats = clean_data(df_raw, logger=logger)
        df_clean.to_csv(STAGING_DIR / "food_delivery_staging.csv", index=False)

    with Timer("feature_engineering", timings, logger=logger):
        df_fe = feature_engineering(df_clean, logger=logger)

    with Timer("outliers", timings, logger=logger):
        df_out, outlier_report = handle_outliers_iqr(df_fe, logger=logger)
        df_out.to_csv(PROCESSED_DIR / "food_delivery_processed.csv", index=False)

    with Timer("dw_model", timings, logger=logger):
        dims, fact = build_star_schema(df_out, logger=logger)

    with Timer("load", timings, logger=logger):
        load_to_sqlite(dims, fact, DW_PATH, logger=logger)

    validations = validate_data(df_out, fact=fact)
    assert_validations(validations)

    logger.info("Quality metrics: %s", quality_metrics)
    logger.info("Clean stats: %s", clean_stats)
    logger.info("Outliers (top 5): %s", sorted(outlier_report, key=lambda x: x["outliers"], reverse=True)[:5])
    logger.info("Timings: %s", timings)
    logger.info("ETL finished")


if __name__ == "__main__":
    main()
