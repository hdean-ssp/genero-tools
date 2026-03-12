# Edge cases and special scenarios

FUNCTION function_with_long_params(param1, param2, param3, param4, param5)
	DEFINE param1 VARCHAR(255)
	DEFINE param2 DECIMAL(10,2)
	DEFINE param3 DATETIME YEAR TO SECOND
	DEFINE param4 MONEY(16,2)
	DEFINE param5 BYTE
	DEFINE result INTEGER
	
	LET result = 0
	CALL validate_long_params(param1, param2, param3)
	CALL process_money(param4)
	RETURN result
END FUNCTION

FUNCTION inline_return()
	DEFINE status INTEGER
	LET status = 1
	CALL log_status(status)
	RETURN status
END FUNCTION

FUNCTION function_with_comments(value)
	DEFINE value INTEGER
	DEFINE result STRING
	
	# Another comment
	LET result = "test"
	# Call with inline comment
	CALL validate_string(result)	# Validate the result
	RETURN result  # Return comment
END FUNCTION

FUNCTION mixed_case_FUNCTION(MixedParam)
	DEFINE MixedParam CHAR(10)
	DEFINE Output_Value SMALLINT
	
	LET Output_Value = 1
	CALL Process_Input(MixedParam)
	LET Output_Value = Get_Status()
	RETURN Output_Value
END FUNCTION

FUNCTION complex_call_patterns(input_val)
	DEFINE input_val STRING
	DEFINE result1 INTEGER
	DEFINE result2 STRING
	
	# Multiple call patterns
	CALL initialize_context()
	LET result1 = get_count(input_val)
	LET result2 = format_output(result1)
	CALL finalize_context()
	
	RETURN result1, result2
END FUNCTION

FUNCTION control_flow_calls(value)
	DEFINE value INTEGER
	DEFINE status INTEGER
	
	# Calls within IF statements
	IF validate_input(value) THEN
		CALL process_valid(value)
		LET status = 1
	ELSE
		CALL process_invalid(value)
		LET status = 0
	END IF
	
	# Calls within CASE statements
	CASE get_type(value)
		WHEN 1
			CALL handle_type1(value)
		WHEN 2
			CALL handle_type2(value)
		OTHERWISE
			CALL handle_default(value)
	END CASE
	
	# Calls within WHILE loop
	WHILE check_condition(value)
		CALL process_loop(value)
		LET value = decrement_value(value)
	END WHILE
	
	RETURN status
END FUNCTION

FUNCTION nested_function_calls(param1, param2)
	DEFINE param1 STRING
	DEFINE param2 INTEGER
	DEFINE result STRING
	
	# Nested function calls
	LET result = outer_function(inner_function(param1), param2)
	
	# Calls in conditional expressions
	IF compare_values(transform_data(param1), param2) THEN
		CALL process_match(result)
	END IF
	
	RETURN result
END FUNCTION
