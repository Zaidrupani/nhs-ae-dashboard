SELECT
    MONTHNAME(month_date) AS month_name,
    MONTH(month_date) AS month_num,
    ROUND(AVG(over4hr_type1 * 100.0 / NULLIF(att_type1, 0)), 2) AS avg_breach_rate,
    ROUND(AVG(att_type1), 0) AS avg_attendances
FROM ae_performance
WHERE att_type1 > 0
GROUP BY month_name, month_num
ORDER BY month_num;