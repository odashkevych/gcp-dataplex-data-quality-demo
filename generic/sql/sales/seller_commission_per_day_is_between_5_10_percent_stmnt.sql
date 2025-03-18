select a.* from data a
        INNER JOIN
          (SELECT
            (SUM(s.commission) / SUM(s.pricepaid)) * 100 AS commission_percentage,
            DATE(s.saletime) AS sale_date,
            sellerid,
          FROM
            `market_sales.sales` s
          GROUP BY
            s.sellerid,
            DATE(s.saletime)) agg_data ON a.sellerid = agg_data.sellerid AND DATE(a.saletime) = agg_data.sale_date
        WHERE not(commission_percentage BETWEEN 5 AND 10)