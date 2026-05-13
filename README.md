# Food Delivery ETL Pipeline

Pipeline academico de ingenieria de datos con ETL, data warehouse en SQLite y analitica basica.

## Arquitectura
- data/raw: CSV original
- data/staging: datos limpios parciales y reportes
- data/processed: dataset transformado
- data/warehouse: SQLite con esquema estrella

Ver detalles en:
- docs/arquitectura.md
- docs/data_dictionary.md
- docs/star_schema.md

## Tecnologias
- Python 3
- pandas, numpy
- SQLAlchemy + SQLite
- matplotlib, seaborn

## Ejecucion
1. Instalar dependencias

```bash
pip install -r requirements.txt
```

2. Ejecutar ETL

```bash
python main.py
```

## Salidas principales
- data/staging/food_delivery_staging.csv
- data/processed/food_delivery_processed.csv
- data/staging/quality_report.csv
- data/warehouse/food_delivery_dw.sqlite
- logs/etl.log

## Metricas ETL
- filas procesadas
- duplicados eliminados
- porcentaje de limpieza
- memoria antes/despues
- tiempos por fase

## Estructura del proyecto
```
food-delivery/
├── data/
│   ├── raw/
│   ├── staging/
│   ├── processed/
│   └── warehouse/
├── docs/
├── logs/
├── notebooks/
├── src/
├── requirements.txt
├── README.md
└── main.py
```
