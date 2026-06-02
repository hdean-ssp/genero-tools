#----------------------------------------------------------------------------
#  Program      : customer_db.4gl
#  Description  : Customer database operations
#----------------------------------------------------------------------------
#  Modifications:
# Ref        Date            Author          Description
#EH100800    15/01/2025      hdean           Initial database layer
#EH100820    10/03/2025      greg            Added count query
#----------------------------------------------------------------------------

FUNCTION customer_insert(p_rec)
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    # WARN: no duplicate check before insert
    CALL log_message("DB insert: " || p_rec.cus_name)
    CALL db_execute_insert("customer", p_rec)
END FUNCTION

FUNCTION customer_update(p_cus_id, p_rec)
    DEFINE p_cus_id INTEGER
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    CALL log_message("DB update: cus_id=" || p_cus_id)
    CALL db_execute_update("customer", p_cus_id, p_rec)
END FUNCTION

FUNCTION customer_remove(p_cus_id)
    DEFINE p_cus_id INTEGER

    CALL log_message("DB delete: cus_id=" || p_cus_id)
    CALL db_execute_delete("customer", p_cus_id)
END FUNCTION

FUNCTION customer_exists(p_cus_id)
    DEFINE p_cus_id INTEGER
    DEFINE l_count INTEGER

    LET l_count = db_count("customer", "cus_id", p_cus_id)
    RETURN (l_count > 0)
END FUNCTION

FUNCTION customer_load(p_cus_id, p_rec)
    DEFINE p_cus_id INTEGER
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    CALL log_message("DB load: cus_id=" || p_cus_id)
    CALL db_select_by_id("customer", p_cus_id, p_rec)
END FUNCTION

# TODO: add LIMIT/OFFSET support for large datasets
FUNCTION customer_load_by_name(p_name, p_results)
    DEFINE p_name STRING
    DEFINE p_results DYNAMIC ARRAY OF RECORD
        cus_id INTEGER,
        cus_name STRING,
        cus_email STRING
    END RECORD

    CALL log_message("DB search: name LIKE " || p_name)
    CALL db_select_by_field("customer", "cus_name", p_name, p_results)
END FUNCTION

FUNCTION customer_count_by_name(p_name)
    DEFINE p_name STRING
    DEFINE l_count INTEGER

    LET l_count = db_count_like("customer", "cus_name", p_name)
    RETURN l_count
END FUNCTION
