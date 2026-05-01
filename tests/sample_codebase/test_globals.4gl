# Test file for GLOBALS and IMPORT parsing edge cases

GLOBALS "rsk_glob.4gl"                                                                     # 46537
GLOBALS "cus_glob.4gl"
GLOBALS "hhr_glob.4gl"

IMPORT FGL lib_utils
IMPORT FGL "lib_common"

GLOBALS "rsk_glob.4gl"                                    #PM05578c

GLOBALS
	DEFINE g_status INTEGER
END GLOBALS

FUNCTION test_func(param1)
	DEFINE param1 INTEGER
	RETURN param1
END FUNCTION
