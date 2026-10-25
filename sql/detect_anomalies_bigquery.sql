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
    current.usage_date,
    current.service,
    current.daily_cost,
    ARRAY(
      SELECT AS STRUCT prior.daily_cost, prior.usage_date
      FROM service_daily AS prior
      WHERE prior.service = current.service
        AND prior.usage_date >= DATE_SUB(current.usage_date, INTERVAL 14 DAY)
        AND prior.usage_date < current.usage_date
      ORDER BY prior.daily_cost, prior.usage_date
    ) AS prior_days
  FROM service_daily AS current
),
baselines AS (
  SELECT
    usage_date,
    service,
    daily_cost,
    ARRAY_LENGTH(prior_days) AS history_days,
    ROUND((prior_days[OFFSET(6)].daily_cost + prior_days[OFFSET(7)].daily_cost) / 2, 2) AS median_cost
  FROM history
  WHERE ARRAY_LENGTH(prior_days) = 14
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
