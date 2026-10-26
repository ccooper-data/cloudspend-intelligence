-- CloudSpend Intelligence V1 detector (SQLite-compatible).
-- Flag a service when daily cost exceeds its trailing 14-day median by both
-- 50% (strictly greater) and $25 (strictly greater).
-- The baseline excludes the current day and requires all 14 prior daily totals.
WITH RECURSIVE
service_daily AS (
    SELECT usage_date, service, ROUND(SUM(cost), 2) AS daily_cost
    FROM billing_records
    GROUP BY usage_date, service
),
history AS (
    SELECT
        current.usage_date,
        current.service,
        current.daily_cost,
        prior.daily_cost AS prior_cost,
        ROW_NUMBER() OVER (
            PARTITION BY current.usage_date, current.service
            ORDER BY prior.daily_cost, prior.usage_date
        ) AS value_rank,
        COUNT(prior.usage_date) OVER (
            PARTITION BY current.usage_date, current.service
        ) AS history_days
    FROM service_daily current
    LEFT JOIN service_daily prior
      ON prior.service = current.service
     AND prior.usage_date >= date(current.usage_date, '-14 days')
     AND prior.usage_date < current.usage_date
),
baselines AS (
    SELECT
        usage_date,
        service,
        daily_cost,
        history_days,
        AVG(CASE WHEN value_rank IN (7, 8) THEN prior_cost END) AS median_cost
    FROM history
    GROUP BY usage_date, service, daily_cost, history_days
),
flagged AS (
    SELECT
        usage_date,
        service,
        daily_cost,
        median_cost,
        ROUND(daily_cost - median_cost, 2) AS absolute_increase,
        ROUND((daily_cost - median_cost) / median_cost * 100.0, 2) AS percent_increase
    FROM baselines
    WHERE history_days = 14
      AND median_cost > 0
      AND daily_cost > median_cost * 1.50
      AND daily_cost - median_cost > 25.00
)
SELECT * FROM flagged ORDER BY usage_date, service;

