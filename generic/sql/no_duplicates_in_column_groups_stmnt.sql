select a.*
from data a
         inner join (select $column_names
                     from data
                     group by $column_names
                     having count (*) > 1) duplicates
                    using ($column_names)