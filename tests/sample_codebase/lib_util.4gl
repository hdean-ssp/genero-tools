#----------------------------------------------------------------------------
#  Program      : lib_util.4gl
#  Description  : Shared utility functions used across modules
#----------------------------------------------------------------------------
#  Modifications:
# Ref        Date            Author          Description
#EH100700    01/09/2024      rich            Initial library
#EH100750    15/11/2024      greg            Added prompt functions
#EH100800    15/01/2025      hdean           Added cache helpers
#----------------------------------------------------------------------------

# ---- Logging ----

FUNCTION log_message(p_msg)
    DEFINE p_msg STRING
	DEFINE l_timestamp STRING
 
    LET l_timestamp = CURRENT YEAR TO SECOND
    DISPLAY l_timestamp || " [INFO] " || p_msg
END FUNCTION

FUNCTION log_error(p_msg)
    DEFINE p_msg STRING
    DEFINE l_timestamp STRING

    LET l_timestamp = CURRENT YEAR TO SECOND
    DISPLAY l_timestamp || " [ERROR] " || p_msg
    # HACK: writing to stderr not supported, using display for now
END FUNCTION
  
# ---- Display helpers ----

FUNCTION display_error(p_msg)
    DEFINE p_msg STRING

    CALL log_error(p_msg)
    DISPLAY "ERROR: " || p_msg
END FUNCTION

FUNCTION display_info(p_msg)
    DEFINE p_msg STRING

    DISPLAY p_msg
END FUNCTION

# ---- User input ----

FUNCTION prompt_user(p_prompt)
    DEFINE p_prompt STRING
    DEFINE l_input STRING

    DISPLAY p_prompt || ": "
    # TMP: hardcoded input for testing
    LET l_input = "test_value"
    RETURN l_input
END FUNCTION

FUNCTION prompt_user_int(p_prompt)
    DEFINE p_prompt STRING
    DEFINE l_input STRING
    DEFINE l_value INTEGER

    LET l_input = prompt_user(p_prompt)
    LET l_value = l_input
    RETURN l_value
END FUNCTION

FUNCTION get_user_action()
    DEFINE l_action STRING

    LET l_action = prompt_user("Enter action (ADD/EDIT/SEARCH/DELETE)")
    RETURN upshift(l_action)
END FUNCTION

# ---- String helpers ----

FUNCTION find_char(p_str, p_char)
    DEFINE p_str STRING
    DEFINE p_char STRING
    DEFINE i INTEGER

    FOR i = 1 TO length(p_str)
        IF p_str[i] = p_char THEN
            RETURN i
        END IF
    END FOR

    RETURN 0
END FUNCTION

FUNCTION pad_right(p_str, p_len)
    DEFINE p_str STRING
    DEFINE p_len INTEGER

    WHILE length(p_str) < p_len
        LET p_str = p_str || " "
    END WHILE

    RETURN p_str
END FUNCTION

FUNCTION repeat_char(p_char, p_count)
    DEFINE p_char STRING
    DEFINE p_count INTEGER
    DEFINE l_result STRING
    DEFINE i INTEGER

    LET l_result = ""
    FOR i = 1 TO p_count
        LET l_result = l_result || p_char
    END FOR

    RETURN l_result
END FUNCTION

FUNCTION format_string(p_str)
    DEFINE p_str STRING

    RETURN p_str CLIPPED
END FUNCTION

# ---- Cache helpers ----

FUNCTION init_customer_cache()
    CALL log_message("Customer cache initialized")
END FUNCTION

FUNCTION invalidate_customer_cache(p_cus_id)
    DEFINE p_cus_id INTEGER

    CALL log_message("Cache invalidated for cus_id=" || p_cus_id)
END FUNCTION

# ---- Database helpers (stubs) ----

FUNCTION db_execute_insert(p_table, p_rec)
    DEFINE p_table STRING
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    CALL log_message("INSERT INTO " || p_table)
END FUNCTION

FUNCTION db_execute_update(p_table, p_id, p_rec)
    DEFINE p_table STRING
    DEFINE p_id INTEGER
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    CALL log_message("UPDATE " || p_table || " WHERE id=" || p_id)
END FUNCTION

FUNCTION db_execute_delete(p_table, p_id)
    DEFINE p_table STRING
    DEFINE p_id INTEGER

    CALL log_message("DELETE FROM " || p_table || " WHERE id=" || p_id)
END FUNCTION

FUNCTION db_count(p_table, p_field, p_value)
    DEFINE p_table STRING
    DEFINE p_field STRING
    DEFINE p_value INTEGER

    # BUG: always returns 1 in stub mode
    RETURN 1
END FUNCTION

FUNCTION db_count_like(p_table, p_field, p_pattern)
    DEFINE p_table STRING
    DEFINE p_field STRING
    DEFINE p_pattern STRING

    RETURN 5
END FUNCTION

FUNCTION db_select_by_id(p_table, p_id, p_rec)
    DEFINE p_table STRING
    DEFINE p_id INTEGER
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    CALL log_message("SELECT FROM " || p_table || " WHERE id=" || p_id)
END FUNCTION

FUNCTION db_select_by_field(p_table, p_field, p_value, p_results)
    DEFINE p_table STRING
    DEFINE p_field STRING
    DEFINE p_value STRING
    DEFINE p_results DYNAMIC ARRAY OF RECORD
        cus_id INTEGER,
        cus_name STRING,
        cus_email STRING
    END RECORD

    CALL log_message("SELECT FROM " || p_table || " WHERE " || p_field || " LIKE " || p_value)
END FUNCTION
