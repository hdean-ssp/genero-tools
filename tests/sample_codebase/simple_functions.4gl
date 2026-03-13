#----------------------------------------------------------------------------------------
#  Program      : commshub.42r
#  $Header
#  Date : 20/03/2024                                                            Author  : richard
#----------------------------------------------------------------------------------------
#  Description:
#  Comms Hub Services - Control module.
#
#  ARGS : 1= BB flag                    #TRUE=Black box
#               : 2= Employee ID
#                 3= Service ID                 This is attrib commshub_audit.cha_service_id. (see below)
#         4= Cus ID
#         5= Con ID
#                 6= Rsh ID (opt)               Risk ID (use 0 if service call is not risk based)
#                 7= Job ID (opt)               Job ID of scheduler pack if required (use 0 if not from pack)
#                 8= Dot No (opt)       Doc template number (use 0 if not required)
#                 9= Spl ID (opt)       Spooler ID (use 0 if not required)
#                10= SMS message (opt)  Ad-hoc SMS text
#
#  e.g. commshub.42r 1 SYS 1 3079 12345 0 0 0 = SMS service for customer 3079 contract 12335 (black box)
#
#       Service ID
#   -----------
#       1 = SMS Messaging module
#       2 = Email Messaging module
#       3 = Error Email module
#----------------------------------------------------------------------------------------
#  Modifications:
# Ref        For                Date            Who                     Description
#EH100466-4      1410.05        20/03/2024  Rich                Initial
#EH100539-4      1410.10        30/05/2024      Greg            Ad-hoc SMS Messaging
#EH100512-2  1410.16    19/08/2024      Chilly          Email integration
#PRB-299         1410.16        28/08/2024      MartinB         Enhanced MailMerge Error Handling
#                                                                                       - extra 11th parameter passed to commshub_control
#EH100512-9  1410.16    29/08/2024      Chilly          Job scheduler send file attachments
#PRB-337         1410.17        05/09/2024      MartinB         Removed changes for PRB-299
#EH100512-15 1410.17    06/09/2024  Chris P     Don't run SMS/Email if not active
#EH100512-9a 1410.18    19/09/2024      Chilly          Use job_task_params for commshub for passing file attachments
#EH100512        1410.20    16/10/2024  Chris P     No background form required
#SR-40356-3      1410.30        01/04/2025      Rich            Error email service
#----------------------------------------------------------------------------------------

# Simple functions with basic parameter and return types

FUNCTION add_numbers(a, b)
    DEFINE a INTEGER
    DEFINE b INTEGER
    DEFINE result INTEGER
    
    LET result = a + b
    # Call another function to validate result
    CALL validate_number(result)
    RETURN result
END FUNCTION

FUNCTION get_user_name(user_id)
    DEFINE user_id INTEGER
    DEFINE name STRING
    
    # Some logic here
    LET name = "John Doe"
    # Call library function to format name
    LET name = format_string(name)
    RETURN name
END FUNCTION

FUNCTION no_params_no_return()
    DISPLAY "Hello World"
    # Call utility function
    CALL log_message("Function executed")
END FUNCTION

FUNCTION display_message(msg)
    DEFINE msg STRING
    
    DISPLAY msg
    CALL log_message(msg)
END FUNCTION
