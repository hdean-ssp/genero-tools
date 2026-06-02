#----------------------------------------------------------------------------
#  Program      : report_main.4gl
#  Description  : Reporting module - customer report generation
#----------------------------------------------------------------------------
#  Modifications:
# Ref        Date            Author          Description
#EH100850    01/02/2025      greg            Initial reporting
#----------------------------------------------------------------------------

FUNCTION report_main()
    DEFINE l_type STRING

    CALL log_message("Reporting module started")

    LET l_type = get_user_action()

    CASE l_type
        WHEN "SUMMARY"
            CALL report_customer_summary()
        WHEN "DETAIL"
            CALL report_customer_detail()
        OTHERWISE
            CALL display_error("Unknown report type: " || l_type)
    END CASE

    CALL log_message("Reporting module finished")
END FUNCTION

FUNCTION report_customer_summary()
    DEFINE l_count INTEGER

    CALL log_message("Generating customer summary report")

    # TODO: pull real counts from database
    LET l_count = db_count("customer", "cus_id", 0)

    CALL display_info("Total customers: " || l_count)
    CALL display_separator()
END FUNCTION

FUNCTION report_customer_detail()
    DEFINE l_cus_id INTEGER

    LET l_cus_id = prompt_user_int("Enter customer ID for detail report")

    IF l_cus_id <= 0 THEN
        CALL display_error("Invalid customer ID")
        RETURN
    END IF

    IF NOT customer_exists(l_cus_id) THEN
        CALL display_error("Customer not found: " || l_cus_id)
        RETURN
    END IF

    #TMPHD - stub report output for now
    CALL log_message("Detail report for cus_id=" || l_cus_id)
    CALL display_info("Report generated for customer " || l_cus_id)
END FUNCTION
