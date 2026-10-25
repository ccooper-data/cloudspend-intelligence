-- Fails the BigQuery script if the live synthetic result differs from the
-- deterministic local contract. No real billing data is queried.
ASSERT (
  SELECT COUNT(*) = 540
  FROM `${project_id}.cloudspend_v1.billing_records`
  WHERE is_synthetic = TRUE
) AS 'Expected exactly 540 explicitly synthetic billing records';

ASSERT (
  SELECT COUNT(*) = 2
  FROM `${project_id}.cloudspend_v1.anomalies`
) AS 'Expected exactly two anomalous service-days';

ASSERT (
  SELECT COUNT(*) = 2
  FROM `${project_id}.cloudspend_v1.anomalies`
  WHERE (usage_date = DATE '2025-03-17' AND service = 'Cloud Run'
         AND project_id = 'checkout-prod' AND sku = 'vCPU-seconds')
     OR (usage_date = DATE '2025-03-22' AND service = 'BigQuery'
         AND project_id = 'analytics-prod' AND sku = 'Analysis')
) AS 'Expected deterministic dates, services, projects, and SKUs';

SELECT
  usage_date,
  service,
  daily_cost,
  median_cost,
  absolute_increase,
  percent_increase,
  project_id,
  sku,
  contributor_cost,
  explanation
FROM `${project_id}.cloudspend_v1.anomalies`
ORDER BY usage_date, service;
