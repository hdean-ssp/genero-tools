#----------------------------------------------------------------------------
#  Makefile : customer.m3
#  Date : 15/01/2025                                                         
   Author  : hdean                                                           
#----------------------------------------------------------------------------
#  Description:
#       Customer management module.
#
#----------------------------------------------------------------------------
#  Modifications:
#  Ref        Date            Who             Description
#
#EH100800    15/01/2025      hdean           Initial customer module
#EH100830    18/03/2025      hdean           Added validation
#----------------------------------------------------------------------------

include $(BASE_DEV)/MakeRules

GLOBALS=
GLOBOFILE=

NEW_GLOBS=
NEW_GLOBO=      $(NEW_GLOBS:.4gl=.42o)

L4GLS=          lib_util.4gl

U4GLS=

4GLS=           customer_main.4gl customer_db.4gl customer_validate.4gl customer_display.4gl

CFILES=
ECFILES=

4GLOFILES=      $(4GLS:.4gl=.42o) $(L4GLS:.4gl=.42o) $(U4GLS:.4gl=.42o)
COFILES=        $(CFILES:.c=.o)
ECOFILES=       $(ECFILES:.ec=.o)

PROG_OS=        $(4GLOFILES) $(COFILES) $(ECOFILES)
OFILES=         $(NEW_GLOBO) $(GLOBOFILE) $(PROG_OS) $(PROG_LIBS)
DEPENDANTS=     $(OFILES)

all: customer.4ge

customer.4ge:   $(DEPENDANTS)
	@echo "$(OFILES) -o $@ $(LINK_OPT) $(SYSLIBS) $(GLOB_LD) " > $(OUT_FILE); \
	$(COMPILE_PROG) $(OUT_FILE);

$(PROG_OS):     $(GLOBALS) $(NEW_GLOBO)
