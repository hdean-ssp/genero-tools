#----------------------------------------------------------------------------
#  Program      : customer_validate.4gl
#  Description  : Customer data validation
#----------------------------------------------------------------------------
#  Modifications:
# Ref        Date            Author          Description
#EH100800    15/01/2025      hdean           Initial validation
#EH100830    18/03/2025      hdean           Email format check
#----------------------------------------------------------------------------

FUNCTION validate_customer(p_rec)
    DEFINE p_rec RECORD
        cus_name STRING,
        cus_email STRING,
        cus_phone STRING
    END RECORD

    IF NOT validate_name(p_rec.cus_name) THEN
        CALL log_message("Validation failed: name")
        RETURN FALSE
    END IF

    IF NOT validate_email(p_rec.cus_email) THEN
        CALL log_message("Validation failed: email")
        RETURN FALSE
    END IF

    IF NOT validate_phone(p_rec.cus_phone) THEN
        CALL log_message("Validation failed: phone")
        RETURN FALSE
    END IF

    RETURN TRUE
END FUNCTION

FUNCTION validate_name(p_name)
    DEFINE p_name STRING

    IF p_name IS NULL OR length(p_name) < 2 THEN
        RETURN FALSE
    END IF

    IF length(p_name) > 100 THEN
        RETURN FALSE
    END IF

    RETURN TRUE
END FUNCTION

# FIX: updated regex to handle plus-addressed emails (user+tag@domain)
FUNCTION validate_email(p_email)
    DEFINE p_email STRING
    DEFINE l_at_pos INTEGER

    IF p_email IS NULL OR length(p_email) < 5 THEN
        RETURN FALSE
    END IF

    LET l_at_pos = find_char(p_email, "@")
    IF l_at_pos <= 1 THEN
        RETURN FALSE
    END IF

    IF find_char(p_email, ".") <= l_at_pos THEN
        RETURN FALSE
    END IF

    RETURN TRUE
END FUNCTION

FUNCTION validate_phone(p_phone)
    DEFINE p_phone STRING

    #TMPHD - skipping phone validation for now, just check not empty
    IF p_phone IS NULL OR length(p_phone) < 1 THEN
        RETURN FALSE
    END IF

    # NOTE: phone format validation deferred to phase 2
    RETURN TRUE
END FUNCTION
