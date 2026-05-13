# Star Schema

## Descripcion
El Data Warehouse se organiza en un esquema estrella con una tabla de hechos y cuatro dimensiones. Se priorizan claves surrogate e indices para consultas analiticas.

## Diagrama
```mermaid
erDiagram
    fact_delivery_orders }o--|| dim_date : date_id
    fact_delivery_orders }o--|| dim_customer_segment : customer_segment_id
    fact_delivery_orders }o--|| dim_delivery_conditions : delivery_conditions_id
    fact_delivery_orders }o--|| dim_order_status : order_status_id

    dim_date {
        int date_id
        int order_hour
        string day_of_week
        int month
    }

    dim_customer_segment {
        int customer_segment_id
        int customer_age
        bool premium_customer_flag
        float customer_loyalty_score
    }

    dim_delivery_conditions {
        int delivery_conditions_id
        float traffic_level_score
        float weather_severity_score
        int city_tier
        bool festival_or_weekend_flag
    }

    dim_order_status {
        int order_status_id
        bool cancellation_flag
        bool delayed_delivery_flag
        bool refund_flag
        bool promo_code_used
    }

    fact_delivery_orders {
        int date_id
        int customer_segment_id
        int delivery_conditions_id
        int order_status_id
        float order_value
        float delivery_fee
        float discount_amount
        float tip_amount
        float final_amount_paid
        float delivery_time_minutes
        float preparation_time_minutes
        float customer_rating
        float delivery_efficiency_score
    }
```

## Tabla de hechos
- fact_delivery_orders: metricas de valor, tiempos y calidad de servicio, mas claves foraneas a dimensiones.

## Dimensiones
- dim_date: hora, dia de semana y mes.
- dim_customer_segment: edad, premium y score de fidelidad.
- dim_delivery_conditions: trafico, clima, ciudad y contexto.
- dim_order_status: estados de la orden (cancelacion, retraso, reembolso, promo).
