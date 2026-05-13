# Data Dictionary

## Tabla: food_delivery_analytics_cleaned (raw)
| columna | tipo esperado | descripcion | transformacion |
| --- | --- | --- | --- |
| order_id | string | Identificador unico de la orden | Normalizado a snake_case en nombre de columna |
| city_tier | int | Segmento de ciudad (tier) | Imputacion mediana si aplica |
| customer_age | int | Edad del cliente | Imputacion mediana si aplica |
| customer_loyalty_score | float | Score de fidelidad del cliente | Imputacion mediana si aplica |
| order_hour | int | Hora de la orden | Imputacion mediana si aplica |
| order_day_of_week | int/string | Dia de la semana de la orden | Imputacion mediana o moda |
| order_month | int | Mes de la orden | Imputacion mediana si aplica |
| delivery_distance_km | float | Distancia de entrega en km | Imputacion mediana si aplica |
| preparation_time_minutes | float | Minutos de preparacion | Imputacion mediana si aplica |
| delivery_time_minutes | float | Minutos de entrega | Imputacion mediana si aplica |
| estimated_delivery_time | float | Tiempo estimado de entrega | Imputacion mediana si aplica |
| traffic_level_score | float | Severidad de trafico | Imputacion mediana si aplica |
| weather_severity_score | float | Severidad del clima | Imputacion mediana si aplica |
| restaurant_rating | float | Rating del restaurante | Imputacion mediana si aplica |
| delivery_partner_rating | float | Rating del repartidor | Imputacion mediana si aplica |
| customer_rating | float | Rating del cliente | Imputacion mediana si aplica |
| order_value | float | Valor de la orden | Imputacion mediana si aplica |
| delivery_fee | float | Costo de delivery | Imputacion mediana si aplica |
| discount_amount | float | Descuento aplicado | Imputacion mediana si aplica |
| tip_amount | float | Propina | Imputacion mediana si aplica |
| final_amount_paid | float | Monto final pagado | Imputacion mediana si aplica |
| number_of_items | int | Cantidad de items | Imputacion mediana si aplica |
| cancellation_flag | bool | Indicador de cancelacion | Imputacion moda si aplica |
| delayed_delivery_flag | bool | Indicador de retraso | Imputacion moda si aplica |
| refund_flag | bool | Indicador de reembolso | Imputacion moda si aplica |
| promo_code_used | bool | Uso de promocion | Imputacion moda si aplica |
| premium_customer_flag | bool | Cliente premium | Imputacion moda si aplica |
| festival_or_weekend_flag | bool | Festivo o fin de semana | Imputacion moda si aplica |
| delivery_partner_experience_years | int | Anos de experiencia del repartidor | Imputacion mediana si aplica |
| delivery_efficiency_score | float | Score operativo (si viene en raw) | Imputacion mediana si aplica |

## Columnas derivadas (processed)
| columna | tipo esperado | descripcion | formula |
| --- | --- | --- | --- |
| delivery_time_category | category | Segmento de tiempo de entrega | pd.cut sobre delivery_time_minutes |
| order_value_category | category | Segmento de valor de orden | pd.cut sobre order_value |
| high_traffic_flag | int | Trafico alto | traffic_level_score >= 7 |
| weather_risk_flag | int | Clima riesgoso | weather_severity_score >= 7 |
| customer_loyalty_segment | category | Segmento de fidelidad | cuantiles de customer_loyalty_score |
| discount_percentage | float | % descuento | discount_amount / order_value * 100 |
| tip_percentage | float | % propina | tip_amount / order_value * 100 |
| cost_efficiency_score | float | Eficiencia costo/tiempo | final_amount_paid / delivery_time_minutes |
| peak_hour_flag | int | Hora pico | order_hour en [11,12,13,19,20,21] |
| operational_risk_score | float | Riesgo operativo | trafico + clima + retraso (ponderado) |
