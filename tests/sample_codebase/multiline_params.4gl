# Functions with multi-line parameter declarations

FUNCTION single_line_params(param1, param2)
	DEFINE param1 INTEGER
	DEFINE param2 STRING
	RETURN param1
END FUNCTION

FUNCTION multiline_two_lines(param1,
	param2, param3)
	DEFINE param1 INTEGER
	DEFINE param2 STRING
	DEFINE param3 DECIMAL
	RETURN param1
END FUNCTION

FUNCTION multiline_each_line(
	alpha,
	beta,
	gamma
)
	DEFINE alpha INTEGER
	DEFINE beta STRING
	DEFINE gamma DECIMAL
	RETURN alpha
END FUNCTION

FUNCTION multiline_paren_on_same_line(
	x, y, z)
	DEFINE x INTEGER
	DEFINE y INTEGER
	DEFINE z INTEGER
	RETURN x
END FUNCTION

FUNCTION no_params_multiline()
	DEFINE status INTEGER
	LET status = 1
	RETURN status
END FUNCTION

FUNCTION lib4_win_display_list(p_arrcnt, p_lenf1, p_lenf2, p_lenf3, p_lenf4,
								p_lenf5, p_retfld, p_winsize, p_row, p_col,
								p_def_list_pos)
	DEFINE p_arrcnt INTEGER
	DEFINE p_lenf1 INTEGER
	DEFINE p_lenf2 INTEGER
	DEFINE p_lenf3 INTEGER
	DEFINE p_lenf4 INTEGER
	DEFINE p_lenf5 INTEGER
	DEFINE p_retfld INTEGER
	DEFINE p_winsize INTEGER
	DEFINE p_row INTEGER
	DEFINE p_col INTEGER
	DEFINE p_def_list_pos INTEGER
	RETURN p_arrcnt
END FUNCTION
