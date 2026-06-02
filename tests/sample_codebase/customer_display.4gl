#----------------------------------------------------------------------------
#  Program      : customer_display.4gl
#  Description  : Customer display and formatting
#----------------------------------------------------------------------------
#  Modifications:
# Ref        Date            Author          Description
#EH100800    15/01/2025      hdean           Initial display functions
#----------------------------------------------------------------------------

FUNCTION customer_display_list(p_results)
    DEFINE p_results DYNAMIC ARRAY OF RECORD
        cus_id INTEGER,
        cus_name STRING,
        cus_email STRING
    END RECORD
    DEFINE i INTEGER

    CALL display_info("Found " || p_results.getLength() || " customers:")
    CALL display_separator()

    FOR i = 1 TO p_results.getLength()
        CALL customer_display_row(
            p_results[i].cus_id,
            p_results[i].cus_name,
            p_results[i].cus_email
        )
    END FOR

    CALL display_separator()
END FUNCTION

FUNCTION customer_display_row(p_id, p_name, p_email)
    DEFINE p_id INTEGER
    DEFINE p_name STRING
    DEFINE p_email STRING
    DEFINE l_formatted STRING

    LET l_formatted = format_display_row(p_id, p_name, p_email)
    DISPLAY l_formatted
END FUNCTION

FUNCTION format_display_row(p_id, p_name, p_email)
    DEFINE p_id INTEGER
    DEFINE p_name STRING
    DEFINE p_email STRING

    RETURN p_id USING "####" || "  " || pad_right(p_name, 30) || "  " || p_email
END FUNCTION

FUNCTION display_separator()
    DISPLAY repeat_char("-", 70)
END FUNCTION
