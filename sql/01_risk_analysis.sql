USE credit_risk_portfolio;

-- CTE to calculate a rough "Risk Score" based on recent missed payments
CREATE VIEW vw_risk_summary AS
WITH CustomerRiskScoring AS (
    SELECT 
        id,
        limit_bal AS credit_limit,
        age,
        -- In this dataset, a positive PAY value means months delayed. 
        -- We sum the delays of the most recent 3 months to spot immediate risk.
        (CASE WHEN pay_0 > 0 THEN pay_0 ELSE 0 END + 
         CASE WHEN pay_2 > 0 THEN pay_2 ELSE 0 END + 
         CASE WHEN pay_3 > 0 THEN pay_3 ELSE 0 END) AS recent_delay_score,
        default_payment_next_month AS actually_defaulted
    FROM customer_risk_profiles
)

-- Segment customers and calculate key metrics for Power BI
SELECT 
    CASE 
        WHEN recent_delay_score >= 4 THEN 'High Risk (4+ Months Delayed)'
        WHEN recent_delay_score > 0 THEN 'Medium Risk (1-3 Months Delayed)'
        ELSE 'Low Risk (On Time)'
    END AS risk_tier,
    COUNT(id) AS total_customers,
    ROUND(AVG(credit_limit), 2) AS avg_credit_limit,
    -- Multiplying by 100 turns the binary 0/1 into a percentage rate
    ROUND(AVG(actually_defaulted) * 100, 2) AS default_rate_percentage
FROM CustomerRiskScoring
GROUP BY risk_tier
ORDER BY default_rate_percentage DESC;