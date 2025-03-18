select *
from (select sum(case when ($condition) then 1 else 0 end) * 100 / count(*) as pct
      from data)
where pct < $threshold_pct