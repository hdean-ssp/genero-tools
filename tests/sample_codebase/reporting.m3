#----------------------------------------------------------------------------
#  Makefile : reporting.m3
#  Date : 01/02/2025                                                         
   Author  : greg                                                            
#----------------------------------------------------------------------------
#  Description:
#       Reporting module - generates customer reports.
#
#----------------------------------------------------------------------------
#  Modifications:
#  Ref        Date            Who             Description
#
#EH100850    01/02/2025      greg            Initial reporting module
#----------------------------------------------------------------------------

include $(BASE_DEV)/MakeRules

GLOBALS=
GLOBOFILE=

NEW_GLOBS=
NEW_GLOBO=      $(NEW_GLOBS:.4gl=.42o)

L4GLS=          lib_util.4gl

U4GLS=

4GLS=           report_main.4gl

CFILES=
ECFILES=

4GLOFILES=      $(4GLS:.4gl=.42o) $(L4GLS:.4gl=.42o) $(U4GLS:.4gl=.42o)
COFILES=        $(CFILES:.c=.o)
ECOFILES=       $(ECFILES:.ec=.o)

PROG_OS=        $(4GLOFILES) $(COFILES) $(ECOFILES)
OFILES=         $(NEW_GLOBO) $(GLOBOFILE) $(PROG_OS) $(PROG_LIBS)
DEPENDANTS=     $(OFILES)

all: reporting.4ge

reporting.4ge:  $(DEPENDANTS)
	@echo "$(OFILES) -o $@ $(LINK_OPT) $(SYSLIBS) $(GLOB_LD) " > $(OUT_FILE); \
	$(COMPILE_PROG) $(OUT_FILE);

$(PROG_OS):     $(GLOBALS) $(NEW_GLOBO)
