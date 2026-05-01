SELECT
    parent_org AS region,
    month_date,
    SUM(wait_12plushr_dta) AS total_12hr_waits,
    SUM(att_type1) AS total_attendances,
    ROUND(SUM(wait_12plushr_dta) * 100.0 / NULLIF(SUM(att_type1), 0), 2) AS critical_wait_rate
FROM ae_performance
WHERE att_type1 > 0
GROUP BY region, month_date
ORDER BY region, month_date;