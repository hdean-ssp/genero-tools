FUNCTION process_abi_message(msg LIKE abi_message.*)
    DEFINE msg LIKE abi_message.*
    DEFINE msg_id INTEGER
    
    LET msg_id = msg.msg_id
    
    RETURN msg_id
END FUNCTION

FUNCTION get_message_id(id LIKE abi_message.msg_id)
    DEFINE id LIKE abi_message.msg_id
    
    RETURN id
END FUNCTION

FUNCTION process_segment(seg LIKE abi_segments.*)
    DEFINE seg LIKE abi_segments.*
    
    RETURN seg.seg_id
END FUNCTION

FUNCTION get_field_name(field LIKE abi_fields.field_name)
    DEFINE field LIKE abi_fields.field_name
    
    RETURN field
END FUNCTION
