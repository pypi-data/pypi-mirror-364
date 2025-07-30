from python_sdk_remote.mini_logger import MiniLogger as logger

from .Connector import get_connection
from .MessageSeverity import MessageSeverity
from .SendToLogzIo import SendToLogzIo

COMPUTER_LANGUAGE = "Python"
COMPONENT_ID = 102
COMPONENT_NAME = 'Logger Python'

# TODO update with sql2code
cache = ['logger_id', 'number', 'identifier', 'client_ip_v4', 'client_ip_v6', 'server_ip_v4', 'server_ip_v6',
         'location_id', 'user_id', 'profile_id', 'activity', 'activity_id', 'action_id', 'message', 'record', 'payload',
         'component_id', 'component_name', 'path', 'filename', 'class_name', 'function_name', 'line_number',
         'error_stack', 'severity_id', 'status_id', 'group_id', 'relationship_type_id', 'timestamp', 'state_id',
         'variable_id', 'variable_value_old', 'variable_value_new', 'field_id', 'field_value_old', 'field_value_new',
         'session', 'thread_id', 'process_id', 'api_type', 'api_type_id', 'group_id1', 'group_id2',
         'component_category', 'testing_framework', 'component_type', 'computer_language', 'developer_email',
         'sql_statement', 'sql_parameters', 'sql_formatted', 'smartlink_identifier', 'stdout', 'stderr', 'return_code',
         'returned_value', 'return_message', 'recipient', 'source_email', 'destination_emails', 'message_id',
         'message_template_id', 'criteria_id', 'question_id', 'message_template_text_block_id', 'compound_message',
         'text_block_id', 'reaction_id', 'result', 'real_name', 'user_identifier', 'locals_before_exception',
         'is_assertion_error', 'is_test_data', 'start_timestamp', 'end_timestamp', 'start_datetime', 'end_datetime',
         'created_timestamp', 'created_user_id', 'created_real_user_id', 'created_effective_user_id',
         'created_effective_profile_id', 'updated_timestamp', 'updated_user_id', 'updated_real_user_id',
         'updated_effective_user_id', 'updated_effective_profile_id']


# TODO Rename Fields to LoggerFields
class Fields:
    @staticmethod
    def get_logger_table_fields():
        """Returns the list of columns in the logger table"""
        global cache
        if cache:
            return cache
        # TODO Shall we check LOGGER_IS_WRITE_TO_SQL before doing this query?
        sql_query = "DESCRIBE logger.logger_table"
        logger.info(object={"sql_query": sql_query})
        try:
            object1 = {
                'record': {'severity_id': MessageSeverity.Information.value,
                           'severity_name': MessageSeverity.Information.name,
                           'component_id': COMPONENT_ID,
                           'component_name': COMPONENT_NAME,
                           'computer_language': COMPUTER_LANGUAGE,
                           'message': "get_logger_table_fields activated"},
                'severity_id': MessageSeverity.Information.value,
                'component_id': COMPONENT_ID,
                'severity_name': MessageSeverity.Information.name,
                'component_name': COMPONENT_NAME,
                'COMPUTER_LANGUAGE': COMPUTER_LANGUAGE,
                'message': "get_logger_table_fields activated",
            }
            SendToLogzIo.send_to_logzio(object1)
            con = get_connection(schema_name="logger")
            cursor = con.cursor()
            cursor.execute(sql_query)
            columns_info = cursor.fetchall()
            columns = [column[0] for column in columns_info]
            cache = columns
            return columns

        except Exception as exception:
            logger.exception("logger-local-python-package LoggerService.py sql(self) Exception caught SQL=" +
                             sql_query, exception)
