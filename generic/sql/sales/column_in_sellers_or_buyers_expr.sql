$column in (select sellerid from `$ref_data_dataset.$ref_data_table_id`
        union distinct select buyerid from `$ref_data_dataset.$ref_data_table_id`)