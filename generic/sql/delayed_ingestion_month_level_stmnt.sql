select *
from (select count(*) as n
      from data a
      where date($ingestion_date_month) >= date_sub(current_date(), interval $elapsed_time_months month))
where n = 0