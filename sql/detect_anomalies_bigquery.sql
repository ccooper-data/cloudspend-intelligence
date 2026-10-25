-- BigQuery Standard SQL implementation of the CloudSpend V1 detector.
-- Rebuilds the output table, so retries are idempotent. The current day is
-- excluded from an exact 14-calendar-day trailing median. Both thresholds are
-- strict: greater than 50% AND greater than $25.
CREATE OR REPLACE TABLE `${project_id}.cloudspend_v1.anomalies` AS
WITH service_daily AS (
  SELECT usage_date, service, ROUND(SUM(cost), 2) AS daily_cost
  FROM `${project_id}.cloudspend_v1.billing_records`
  WHERE is_synthetic = TRUE
  GROUP BY usage_date, service
),
history AS (
  SELECT
    cur.usage_date,
    cur.service,
    cur.daily_cost,
    ARRAY_AGG(prior.daily_cost IGNORE NULLS ORDER BY prior.daily_cost, prior.usage_date) AS prior_costs,
    COUNT(prior.usage_date) AS history_days
  FROM service_daily AS cur
  LEFT JOIN service_daily AS prior
    ON prior.service = cur.service
   AND prior.usage_date >= DATE_SUB(cur.usage_date, INTERVAL 14 DAY)
   AND prior.usage_date < cur.usage_date
  GROUP BY cur.usage_date, cur.service, cur.daily_cost
),
baselines AS (
  SELECT
    usage_date,
    service,
    daily_cost,
    history_days,
    ROUND((prior_costs[OFFSET(6)] + prior_costs[OFFSET(7)]) / 2, 2) AS median_cost
  FROM history
  WHERE history_days = 14
),
flagged AS (
  SELECT
    usage_date,
    service,
    daily_cost,
    median_cost,
    ROUND(daily_cost - median_cost, 2) AS absolute_increase,
    ROUND(SAFE_DIVIDE(daily_cost - median_cost, median_cost) * 100, 2) AS percent_increase
  FROM baselines
  WHERE median_cost > 0
    AND daily_cost > median_cost * 1.50
    AND daily_cost - median_cost > 25.00
),
contributors AS (
  SELECT
    usage_date,
    service,
    project_id,
    sku,
    ROUND(SUM(cost), 2) AS contributor_cost
  FROM `${project_id}.cloudspend_v1.billing_records`
  WHERE is_synthetic = TRUE
  GROUP BY usage_date, service, project_id, sku
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY usage_date, service
    ORDER BY contributor_cost DESC, project_id ASC, sku ASC
  ) = 1
)
SELECT
  flagged.usage_date,
  flagged.service,
  flagged.daily_cost,
  flagged.median_cost,
  flagged.absolute_increase,
  flagged.percent_increase,
  contributors.project_id,
  contributors.sku,
  contributors.contributor_cost,
  FORMAT(
    'On %s, %s spend was $%.2f, up %.2f%% ($%.2f) from its trailing 14-day median of $%.2f. The largest same-day contributor was project %s / SKU %s at $%.2f.',
    CAST(flagged.usage_date AS STRING), flagged.service, flagged.daily_cost,
    flagged.percent_increase, flagged.absolute_increase, flagged.median_cost,
    contributors.project_id, contributors.sku, contributors.contributor_cost
  ) AS explanation,
  'v1.0.0' AS detector_version
FROM flagged
JOIN contributors USING (usage_date, service)
ORDER BY usage_date, service;
