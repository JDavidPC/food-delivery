# Hipótesis y KPIs del Negocio de Food Delivery

## Introducción
Este documento define 4 hipótesis estadísticas y 7 KPIs empresariales para el análisis del negocio de entrega de comida. Cada hipótesis y KPI está alineado con objetivos de negocio, sostenido por datos del warehouse y permite tomar decisiones estratégicas sobre operaciones, costos y satisfacción del cliente.

---

## HIPÓTESIS ESTADÍSTICAS

### Hipótesis 1: Impacto de Horas Pico en el Tiempo de Entrega

**Pregunta de negocio:**  
¿Las horas pico (11-13, 19-21) generan tiempos de entrega significativamente mayores que las horas no pico?

**Justificación de importancia:**  
En operaciones de delivery, las horas pico concentran la mayoría de órdenes. Si los tiempos se degradan notablemente, esto impacta la satisfacción del cliente, genera más cancelaciones, y reduce la eficiencia operativa. Entender esta relación permite dimensionar mejor la flota y mejorar la experiencia de usuario.

**Hipótesis Nula (H₀):**  
$$H_0: \mu_{delivery\_time|peak} = \mu_{delivery\_time|non-peak}$$  
*No hay diferencia significativa en el tiempo de entrega medio entre horas pico y no pico.*

**Hipótesis Alternativa (H₁):**  
$$H_1: \mu_{delivery\_time|peak} > \mu_{delivery\_time|non-peak}$$  
*El tiempo de entrega medio en horas pico es significativamente mayor.*

**Prueba estadística:**  
T-test independiente (dos colas) o Mann-Whitney U si no hay normalidad. α = 0.05.

**Fuentes del warehouse:**  
- `fact_delivery_orders.delivery_time_minutes`  
- `dim_date.order_hour`  
- Derivada: `peak_hour_flag` (order_hour ∈ {11, 12, 13, 19, 20, 21})

**Implicación de negocio si H₁ se rechaza:**  
Ratios de recursos son adecuados; enfoque en otras áreas.

**Implicación de negocio si H₁ se confirma:**  
Invertir en incrementar la capacidad operativa durante horas pico (más repartidores, mejora de logística).

---

### Hipótesis 2: Relación entre Condiciones Operativas (Tráfico, Clima) y Costo de Operación

**Pregunta de negocio:**  
¿Las condiciones adversas de tráfico y clima incrementan significativamente el delivery_fee?

**Justificación de importancia:**  
El costo de entrega es una métrica crítica de rentabilidad. Si tráfico y clima severo incrementan costos de forma no predecible, la empresa debe ajustar precios dinámicos o redimensionar rutas. Esto es crucial para márgenes de ganancia.

**Hipótesis Nula (H₀):**  
$$H_0: \text{delivery\_fee} \text{ es independiente de } (traffic\_level\_score, weather\_severity\_score)$$  
*No existe relación significativa entre condiciones operativas y costo de entrega.*

**Hipótesis Alternativa (H₁):**  
$$H_1: \text{delivery\_fee} \text{ aumenta significativamente con } traffic + weather$$  
*Mayor tráfico y clima severo elevan el delivery_fee de forma estadísticamente significativa.*

**Prueba estadística:**  
Regresión lineal múltiple. Coeficientes significativos (p < 0.05) para traffic_level_score y weather_severity_score.

**Fuentes del warehouse:**  
- `fact_delivery_orders.delivery_fee`  
- `dim_delivery_conditions.traffic_level_score`  
- `dim_delivery_conditions.weather_severity_score`

**Implicación de negocio si H₁ se confirma:**  
Implementar precios dinámicos basados en condiciones operativas. Mejorar la predictibilidad de costos y márgenes.

**Implicación de negocio si H₁ se rechaza:**  
El pricing actual es desacoplado de condiciones; revisar si hay subsidios o ineficiencias ocultas.

---

### Hipótesis 3: Diferencia en Satisfacción entre Clientes Premium y No-Premium

**Pregunta de negocio:**  
¿Los clientes premium tienen ratings de satisfacción (customer_rating) significativamente mayores que los no-premium?

**Justificación de importancia:**  
El programa premium es una fuente de ingresos importante. Validar que exista diferencia en satisfacción justifica la inversión en beneficios premium y permite segmentar mejor la experiencia de usuario.

**Hipótesis Nula (H₀):**  
$$H_0: \mu_{customer\_rating|premium} = \mu_{customer\_rating|non-premium}$$  
*No hay diferencia significativa en el rating promedio entre clientes premium y no-premium.*

**Hipótesis Alternativa (H₁):**  
$$H_1: \mu_{customer\_rating|premium} > \mu_{customer\_rating|non-premium}$$  
*Los clientes premium tienen ratings significativamente mayores.*

**Prueba estadística:**  
T-test independiente (dos colas). α = 0.05.

**Fuentes del warehouse:**  
- `fact_delivery_orders.customer_rating`  
- `dim_customer_segment.premium_customer_flag`

**Implicación de negocio si H₁ se confirma:**  
Mantener y expandir programa premium; diferenciación de servicio es efectiva.

**Implicación de negocio si H₁ se rechaza:**  
Los beneficios premium no generan percepción de valor; revisar beneficios o inversión en experiencia.

---

### Hipótesis 4: Efecto del Descuento en la Tasa de Cancelación

**Pregunta de negocio:**  
¿Las órdenes con descuento tienen una tasa de cancelación significativamente menor que las sin descuento?

**Justificación de importancia:**  
Los descuentos son usados como herramienta de retención y para impulsar volumen. Si no reducen cancelaciones, el ROI de descuentos es negativo. Esta hipótesis valida la estrategia de promociones.

**Hipótesis Nula (H₀):**  
$$H_0: p_{cancel|discount} = p_{cancel|no\_discount}$$  
*La tasa de cancelación es igual para órdenes con y sin descuento.*

**Hipótesis Alternativa (H₁):**  
$$H_1: p_{cancel|discount} < p_{cancel|no\_discount}$$  
*Las órdenes con descuento tienen tasa de cancelación significativamente menor.*

**Prueba estadística:**  
Chi-cuadrado de independencia. α = 0.05.

**Fuentes del warehouse:**  
- `dim_order_status.cancellation_flag`  
- `dim_order_status.promo_code_used` (proxy de descuento; alternativamente, `discount_amount > 0`)

**Implicación de negocio si H₁ se confirma:**  
Descuentos son efectivos para reducir cancelaciones; escalarlos es estratégico.

**Implicación de negocio si H₁ se rechaza:**  
Descuentos no impactan cancelaciones; investigar otros drivers (calidad de selección, tiempo de entrega).

---

## KPIs EMPRESARIALES

### KPI 1: Tiempo Promedio de Entrega (ADT - Average Delivery Time)

**Definición:**  
$$ADT = \frac{\sum delivery\_time\_minutes}{n\_ordenes}$$

**Fórmula SQL (warehouse):**  
```sql
SELECT AVG(delivery_time_minutes) as adt_minutes
FROM fact_delivery_orders;
```

**Unidad:** minutos

**Target:** ≤ 35 minutos (objetivo típico en industria)

**Justificación de negocio:**  
- **Satisfacción del cliente:** entregas rápidas incrementan ratings y retención.
- **Eficiencia operativa:** menor tiempo = más entregas por repartidor = mayor throughput.
- **Competitividad:** tiempo de entrega es diferenciador clave vs. competencia.

**Relación con hipótesis:**  
- **Hipótesis 1 (peak vs. non-peak):** ADT es métrica principal para validar si horas pico degradan tiempos.

**Acción si KPI baja (< 35 min):**  
✓ Mantener operaciones; comunicar ventaja competitiva.

**Acción si KPI sube (> 35 min):**  
✗ Investigar cuellos de botella (tráfico, falta de repartidores, procesos lentos).

---

### KPI 2: Razón de Eficiencia de Costos (Cost Efficiency Ratio)

**Definición:**  
$$CER = \frac{\sum final\_amount\_paid}{\sum delivery\_fee + discount\_amount}$$  
*Relación entre ingresos y costos directos operativos.*

**Fórmula SQL (warehouse):**  
```sql
SELECT 
    SUM(final_amount_paid) / (SUM(delivery_fee) + SUM(discount_amount)) as cost_efficiency_ratio
FROM fact_delivery_orders;
```

**Unidad:** ratio (adimensional, típicamente > 1.5)

**Target:** ≥ 1.8 (ingresos netos al menos 1.8x costos directos)

**Justificación de negocio:**  
- **Rentabilidad:** métrica clave de margen bruto; si CER < 1.5, negocio no es sostenible.
- **Decisiones de pricing:** permite ajustar delivery_fee y discount_amount dinámicamente.
- **Escalabilidad:** CER > 1.8 deja margen para marketing, overhead, inversión.

**Relación con hipótesis:**  
- **Hipótesis 2 (condiciones operativas vs. costo):** CER se verá afectado si tráfico/clima incrementan delivery_fee sin cambio en ingresos.

**Acción si KPI baja (< 1.5):**  
✗ Crisis: revisar pricing, reducir descuentos, optimizar delivery_fee.

**Acción si KPI sube (> 1.8):**  
✓ Oportunidad: invertir en crecimiento, marketing, o tecnología.

---

### KPI 3: Puntuación de Satisfacción del Cliente (CSAT)

**Definición:**  
$$CSAT = \frac{\sum customer\_rating}{n\_ordenes}$$

**Fórmula SQL (warehouse):**  
```sql
SELECT AVG(customer_rating) as csat
FROM fact_delivery_orders;
```

**Unidad:** escala (típicamente 1-5 estrellas)

**Target:** ≥ 4.3 estrellas (top quartile en industria)

**Justificación de negocio:**  
- **Retención:** CSAT > 4.0 incrementa repeat purchase rate en ~30%.
- **Reputación y reviews:** high CSAT genera reviews positivos, atrae nuevos clientes.
- **NPS correlado:** ratings altos correlacionan con Net Promoter Score elevado.
- **Diferenciación:** en mercado competitivo, CSAT es ventaja clave.

**Relación con hipótesis:**  
- **Hipótesis 3 (premium vs. non-premium):** permite validar si programa premium genera diferencia en CSAT.
- **Hipótesis 1 (peak hours):** tiempos de entrega mayores degradan CSAT.

**Acción si KPI baja (< 4.0):**  
✗ Investigar drivers: tiempo de entrega, calidad de comida, comportamiento de repartidor.

**Acción si KPI sube (> 4.5):**  
✓ Comunicar fortaleza; usar en marketing; expandir base de clientes.

---

### KPI 4: Tasa de Cancelación de Órdenes (OCR - Order Cancellation Rate)

**Definición:**  
$$OCR = \frac{n\_cancelled\_orders}{n\_total\_orders} \times 100\%$$

**Fórmula SQL (warehouse):**  
```sql
SELECT 
    (CAST(SUM(CASE WHEN cancellation_flag = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 as ocr_percent
FROM fact_delivery_orders;
```

**Unidad:** porcentaje

**Target:** ≤ 5% (industry benchmark ~3-6%)

**Justificación de negocio:**  
- **Ingresos perdidos:** cada cancelación es ingreso NO realizado (oportunidad perdida).
- **Costo oculto:** repartidor fue asignado, se consumió tiempo de sistema, creó fricción de usuario.
- **Churn predictor:** alto OCR correlaciona con baja retención de clientes.
- **Eficiencia:** reducir OCR directamente incrementa throughput y rentabilidad.

**Relación con hipótesis:**  
- **Hipótesis 4 (descuentos vs. cancelación):** OCR total se beneficia si descuentos reducen cancelaciones.
- **Hipótesis 1 (peak hours):** cancelaciones pueden ser mayores en horas pico si entregas se retrasan.

**Acción si KPI sube (> 6%):**  
✗ Investigar causas: tiempos de entrega, disponibilidad de opciones, pago rechazado, cambio de cliente.

**Acción si KPI baja (< 3%):**  
✓ Benchmarking competitivo; oportunidad de comunicar confiabilidad.

---

### KPI 5: Desempeño Hora Pico vs. No-Pico (Peak vs. Off-Peak Ratio)

**Definición:**  
$$PvOP\_Ratio = \frac{ADT_{peak}}{ADT_{non-peak}}$$

**Fórmula SQL (warehouse):**  
```sql
SELECT 
    (SELECT AVG(delivery_time_minutes) FROM fact_delivery_orders 
     WHERE date_id IN (SELECT date_id FROM dim_date WHERE order_hour IN (11, 12, 13, 19, 20, 21))) AS adt_peak,
    (SELECT AVG(delivery_time_minutes) FROM fact_delivery_orders 
     WHERE date_id NOT IN (SELECT date_id FROM dim_date WHERE order_hour IN (11, 12, 13, 19, 20, 21))) AS adt_non_peak;
-- Ratio = adt_peak / adt_non_peak
```

**Unidad:** ratio

**Target:** ≤ 1.2 (máximo 20% degradación en horas pico)

**Justificación de negocio:**  
- **Capacidad operativa:** indica si infraestructura de repartidores es suficiente.
- **Calidad de experiencia:** si ratio es alto, clientes en horas pico reciben mala experiencia.
- **Decisiones de staffing:** permite dimensionar turnos y contratación.
- **Predictibilidad:** métrica clara para comunicar a stakeholders.

**Relación con hipótesis:**  
- **Hipótesis 1 (peak vs. non-peak):** este KPI es la manifestación directa de H1.

**Acción si KPI sube (> 1.3):**  
✗ Crítico: agregar recursos, mejorar rutas, considerar incentivos dinámicos.

**Acción si KPI es estable (1.0-1.2):**  
✓ Operaciones balanceadas; mantener nivel de servicio.

---

### KPI 6: ROI de Clientes Premium (Premium Customer ROI)

**Definición:**  
$$Premium\_ROI = \frac{(\sum final\_amount\_paid|premium) - (\sum delivery\_fee|premium)}{n\_premium\_customers}$$  
*Ingreso neto promedio por cliente premium.*

**Fórmula SQL (warehouse):**  
```sql
SELECT 
    (SUM(f.final_amount_paid) - SUM(f.delivery_fee)) / COUNT(DISTINCT f.customer_segment_id) as premium_roi
FROM fact_delivery_orders f
JOIN dim_customer_segment cs ON f.customer_segment_id = cs.customer_segment_id
WHERE cs.premium_customer_flag = 1;
```

**Unidad:** moneda (e.g., USD/cliente)

**Target:** Premium_ROI ≥ 1.5 × Non-Premium_ROI (clientes premium generan 50% más valor)

**Justificación de negocio:**  
- **Segmentación estratégica:** valida que inversión en beneficios premium se justifica.
- **LTV (Lifetime Value):** premium customers típicamente tienen higher LTV.
- **Rentabilidad marginal:** permite decidir si expandir programa o redimensionarlo.
- **Diferenciación:** premium tier es fuente de ingresos de alto margen.

**Relación con hipótesis:**  
- **Hipótesis 3 (premium vs. non-premium satisfaction):** si Premium_ROI es alto y CSAT_premium > CSAT_non_premium, el programa es exitoso.

**Acción si KPI baja (< 1.3x):**  
✗ Programa premium no genera valor suficiente; revisar beneficios o inversión.

**Acción si KPI sube (> 1.5x):**  
✓ Expandir programa; considerar tier adicional (ultra-premium).

---

### KPI 7: Índice de Riesgo Operativo (ORI - Operational Risk Index)

**Definición:**  
$$ORI = \frac{\sum operational\_risk\_score}{n\_ordenes}$$  
*Promedio ponderado de riesgos operativos (tráfico, clima, retrasos).*

**Fórmula SQL (warehouse):**  
```sql
SELECT 
    AVG(operational_risk_score) as ori
FROM fact_delivery_orders;
```

**Donde** `operational_risk_score` (derivada en ETL):  
$$operational\_risk\_score = (traffic\_level\_score \times 0.4) + (weather\_severity\_score \times 0.4) + (delayed\_delivery\_flag \times 10 \times 0.2)$$

**Unidad:** puntuación (0-10 escala)

**Target:** ≤ 4.5 (riesgo medio bajo)

**Justificación de negocio:**  
- **Previsibilidad:** métrica agregada de incertidumbre en operaciones.
- **Pricing dinámico:** ORI alto justifica incremento de delivery_fee.
- **Resource planning:** ORI alto indica necesidad de aumentar márgenes de tiempo y repartidores.
- **Comunicación:** permite explicar a clientes por qué ciertas órdenes son más caras o lentas.

**Relación con hipótesis:**  
- **Hipótesis 2 (condiciones operativas vs. costo):** ORI alto correlaciona con incremento de delivery_fee.

**Acción si KPI sube (> 5.0):**  
✗ Condiciones operativas adversas; aumentar delivery_fee, buffer de tiempo en estimaciones.

**Acción si KPI baja (< 3.5):**  
✓ Condiciones favorables; oportunidad de reducir tiempos estimados, mejorar margen.

---

## Matriz de Relaciones: Hipótesis ↔ KPIs

| Hipótesis | KPI Relacionado | Impacto |
|-----------|-----------------|--------|
| H1: Peak hours ↑ delivery time | KPI 1 (ADT), KPI 5 (Peak vs Off-Peak), KPI 3 (CSAT) | Alto |
| H2: Conditions ↑ cost | KPI 2 (CER), KPI 7 (ORI) | Alto |
| H3: Premium > satisfaction | KPI 3 (CSAT), KPI 6 (Premium ROI) | Medio-Alto |
| H4: Discount ↓ cancellation | KPI 4 (OCR) | Medio |

---

## Plan de Análisis y Monitoreo

### Frecuencia de análisis
- **Hipótesis:** trimestral (validación estadística).
- **KPIs:** diario (dashboard), semanal (reporte ejecutivo), mensual (análisis detallado).

### Herramientas
- **Querying:** SQL directo en warehouse SQLite.
- **Estadística:** Python (scipy, statsmodels) para pruebas de hipótesis.
- **Visualización:** Matplotlib, Seaborn, Plotly para dashboards.
- **Reporte:** Jupyter Notebooks (hipotesis.ipynb), documentos MD.

### Alertas y Umbrales
- **ADT > 40 min:** investigar inmediatamente.
- **CER < 1.5:** escalada a finanzas.
- **CSAT < 4.0:** task force de calidad.
- **OCR > 7%:** análisis de causa raíz.
- **ORI > 6.0:** considerar suspension de servicio en zona.

---

## Conclusión

Estas 4 hipótesis y 7 KPIs forman un marco de análisis integral que cubre **operaciones, finanzas, y satisfacción del cliente**. Su validación y monitoreo continuo permite:
- Tomar decisiones basadas en datos (data-driven).
- Identificar oportunidades de mejora rápidamente.
- Comunicar desempeño a stakeholders con métricas claras.
- Escalar el negocio de forma sostenible y rentable.

Cada hipótesis y KPI está alineado con el warehouse, es medible, y tiene implicación directa en el negocio.
