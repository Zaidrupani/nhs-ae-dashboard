WITH yearly AS (
    SELECT
        org_name,
        YEAR(month_date) AS yr,
        ROUND(SUM(over4hr_type1) * 100.0 / NULLIF(SUM(att_type1), 0), 2) AS annual_breach_rate
    FROM ae_performance
    WHERE att_type1 > 0
    GROUP BY org_name, yr
)
SELECT
    a.org_name,
    a.annual_breach_rate AS rate_2024,
    b.annual_breach_rate AS rate_2025,
    ROUND(b.annual_breach_rate - a.annual_breach_rate, 2) AS change_pct
FROM yearly a
JOIN yearly b ON a.org_name = b.org_name
WHERE a.yr = 2024 AND b.yr = 2025
ORDER BY change_pct DESC;