#----------------------------------------------------------------------------
#  Program      : customer_main.4gl
#  Description  : Customer management - main entry point
#----------------------------------------------------------------------------
#  Modifications:
# Ref        Date            Author          Description
#EH100800    15/01/2025      hdean           Initial customer module
#EH100812    22/02/2025      hdean           Added batch processing
#----------------------------------------------------------------------------

FUNCTION customer_main()
    DEFINE l_action STRING

    CALL log_message("Customer module started")
    CALL init_customer_cache()

    LET l_action = get_user_action()

    CASE l_action
        WHEN "ADD"
            CALL customer_add_new()
        WHEN "EDIT"
            CALL customer_edit()
        WHEN "SEARCH"
            CALL customer_search_by_name("")
        WHEN "DELETE"
            CALL customer_delete()
        OTHERWISE
            CALL display_error("Unknown action: " || l_action)
    END CASE

    CALL log_message("Customer module finished")
END FUNCTION

# TODO: add pagination support for large result sets
FUNCTION customer_search_by_name(p_name)
    DEFINE p_name STRING
    DEFINE l_count INTEGER
    DEFINE l_results DYNAMIC ARRAY OF RECORD
        cus_id INTEGER,
        cus_name STRING,
        con_id LIKE contract.con_id,
        cus_email STRING
END RECORD
	
	LET l_results.cus_id = 1
	LET l_results.cus_name = 1
	LET l_results.cus_email = "test"
    IF p_name IS NULL OR length(p_name) < 1 THEN
        CALL display_error("Search name cannot be empty")
        RETURN
    END IF

    CALL log_message("Searching customers: " || p_name)
    LET l_count = customer_count_by_name(p_name)

    IF l_count = 0 THEN
        CALL display_info("No customers found matching: " || p_name)
        RETURN
    END IF

    # FIXME: this loads all results into memory at once
    CALL customer_load_by_name(p_name, l_results)
    CALL customer_display_list(l_results)
END FUNCTION

FUNCTION customer_add_new()
    DEFINE l_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    CALL log_message("Adding new customer")

    LET l_rec.cus_name = prompt_user("Enter customer name")
    LET l_rec.cus_email = prompt_user("Enter email address")
    LET l_rec.cus_phone = prompt_user("Enter phone number")

    IF NOT validate_customer(l_rec) THEN
        CALL display_error("Invalid customer data")
        RETURN
    END IF

    CALL customer_insert(l_rec)
    CALL log_message("Customer added: " || l_rec.cus_name)
    CALL display_info("Customer created successfully")
END FUNCTION

# BUG: delete does not check for linked contracts before removing
FUNCTION customer_delete()
    DEFINE l_cus_id INTEGER

    LET l_cus_id = prompt_user_int("Enter customer ID to delete")

    IF l_cus_id <= 0 THEN
        CALL display_error("Invalid customer ID")
        RETURN
    END IF

    IF NOT customer_exists(l_cus_id) THEN
        CALL display_error("Customer not found: " || l_cus_id)
        RETURN
    END IF

    CALL customer_remove(l_cus_id)
    CALL invalidate_customer_cache(l_cus_id)
    CALL log_message("Customer deleted: " || l_cus_id)
END FUNCTION

FUNCTION customer_edit()
    DEFINE l_cus_id INTEGER
    DEFINE l_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    LET l_cus_id = prompt_user_int("Enter customer ID to edit")

    IF NOT customer_exists(l_cus_id) THEN
        CALL display_error("Customer not found")
        RETURN
    END IF

    CALL customer_load(l_cus_id, l_rec)

    #TMPHD - temporary debug output for testing edit flow
    CALL log_message("DEBUG editing cus_id=" || l_cus_id)

    LET l_rec.cus_name = prompt_user("Name [" || l_rec.cus_name || "]")
    LET l_rec.cus_email = prompt_user("Email [" || l_rec.cus_email || "]")

    IF NOT validate_customer(l_rec) THEN
        CALL display_error("Invalid customer data")
        RETURN
    END IF

    CALL customer_update(l_cus_id, l_rec)
    CALL invalidate_customer_cache(l_cus_id)
    CALL log_message("Customer updated: " || l_cus_id)
END FUNCTION

# --- Additional functions exercising various record definition forms ---

FUNCTION record_like_table()
    DEFINE l_cust RECORD LIKE customer.*
    LET l_cust.cus_id = 1
    RETURN l_cust.cus_id
END FUNCTION

FUNCTION record_like_table_param(p_rec RECORD LIKE customer.*)
    DEFINE p_rec RECORD LIKE customer.*
    RETURN p_rec.cus_id
END FUNCTION

FUNCTION record_inline_single_field()
    DEFINE l_rec RECORD
        status INTEGER
    END RECORD
    LET l_rec.status = 0
    RETURN l_rec.status
END FUNCTION

FUNCTION record_with_like_fields()
    DEFINE l_rec RECORD
        cus_id LIKE customer.cus_id,
        cus_name LIKE customer.cus_name,
        balance DECIMAL(12,2)
    END RECORD
    LET l_rec.balance = 0.00
    RETURN l_rec.balance
END FUNCTION

FUNCTION record_array_of_record_like()
    DEFINE l_arr DYNAMIC ARRAY OF RECORD LIKE customer.*
    LET l_arr[1].cus_id = 1
    RETURN l_arr[1].cus_id
END FUNCTION

FUNCTION record_dynamic_array_of_record_like()
    DEFINE l_arr DYNAMIC ARRAY OF RECORD LIKE customer.*
    CALL l_arr.appendElement()
    LET l_arr[1].cus_id = 1
    RETURN l_arr[1].cus_id
END FUNCTION

FUNCTION record_nested_types()
    DEFINE l_rec RECORD
        cus_id INTEGER,
        cus_name VARCHAR(200),
        cus_dob DATE,
        cus_created DATETIME YEAR TO SECOND,
        cus_balance MONEY(14,2),
        cus_notes TEXT,
        cus_photo BYTE,
        cus_active BOOLEAN,
        cus_rank SMALLINT,
        cus_score FLOAT,
        cus_ref CHAR(20)
    END RECORD
    LET l_rec.cus_id = 0
    RETURN l_rec.cus_id
END FUNCTION

FUNCTION record_multiple_records()
    DEFINE l_header RECORD
        doc_id INTEGER,
        doc_date DATE
    END RECORD
    DEFINE l_detail RECORD
        line_no INTEGER,
        item_code STRING,
        qty DECIMAL(10,2)
    END RECORD
    DEFINE l_footer RECORD LIKE invoice_footer.*
    LET l_header.doc_id = 1
    LET l_detail.line_no = 1
    RETURN l_header.doc_id
END FUNCTION

FUNCTION record_dynamic_array_inline(p_limit INTEGER)
    DEFINE p_limit INTEGER
    DEFINE l_data DYNAMIC ARRAY OF RECORD
        id INTEGER,
        code CHAR(10),
        description VARCHAR(255),
        amount MONEY(10,2),
        created_at DATETIME YEAR TO FRACTION(3),
        is_active BOOLEAN
    END RECORD
    DEFINE i INTEGER
    FOR i = 1 TO p_limit
        CALL l_data.appendElement()
        LET l_data[i].id = i
        LET l_data[i].code = i
    END FOR
    RETURN l_data.getLength()
END FUNCTION

FUNCTION record_static_array_inline()
    DEFINE l_items ARRAY[50] OF RECORD
        item_id INTEGER,
        item_name STRING,
        item_price DECIMAL(8,2)
    END RECORD
    LET l_items[1].item_id = 1
    RETURN l_items[1].item_id
END FUNCTION

FUNCTION record_mixed_defines()
    DEFINE l_count INTEGER
    DEFINE l_rec RECORD
        field1 STRING,
        field2 INTEGER
    END RECORD
    DEFINE l_name STRING
    DEFINE l_hist DYNAMIC ARRAY OF RECORD
        ts DATETIME YEAR TO SECOND,
        action CHAR(20)
    END RECORD
    DEFINE l_flag BOOLEAN
    LET l_count = 0
    LET l_flag = TRUE
    RETURN l_count
END FUNCTION

FUNCTION record_like_partial_fields()
	DEFINE l_con_id LIKE contract.con_id
    DEFINE l_rec RECORD
        cus_id LIKE customer.cus_id,
        con_id LIKE contract.con_id,
        inv_total LIKE invoice.inv_total,
        notes STRING
    END RECORD
	LET l_con_id = 1
    RETURN l_rec.cus_id
END FUNCTION

FUNCTION record_param_and_local(p_input RECORD LIKE order_header.*)
    DEFINE p_input RECORD LIKE order_header.*
    DEFINE l_line RECORD
        line_no SMALLINT,
        product_id INTEGER,
        quantity DECIMAL(10,3)
    END RECORD
	LET l_line.quantity = 10.321
    DEFINE l_summary RECORD LIKE order_summary.*
    LET l_line.line_no = 1
    RETURN l_line.line_no
END FUNCTION
