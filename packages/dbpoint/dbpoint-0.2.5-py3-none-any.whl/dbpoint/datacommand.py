
from loguru import logger
from .datacolumn import DataColumn
from datetime import datetime
from textops import generate_from_string

class DataCommand():
    """
    Üks SQL (ilma optimeerimata! nt for-tsükkel võib sama alg-def pealt lasta läbi erinevate (või samade) väärtustega mitu SQL-i -- seda hetkel ei vaatle!) 
    """
    def __init__(self, sql_command_or_template: str, rules: dict | None = None):
        self.sql_command_or_template: str = sql_command_or_template
        self.command: str = ""

        self.rules: dict = rules or {} # { 'param_1' : { 'on_empty': 'null' | 'empty', 'surround': 'always' | 'on empty' |'on non-empty' | 'never', 'escape_from': "'", 'escape_to' : "''" } }
        # or: {'param_1' : "ruleset_1"}
        #       and { 'ruleset_1' : { 'on_empty': 'null' | 'empty', 'surround': 'always' | 'on empty' |'on non-empty' | 'never', 'escape_from': "'", 'escape_to' : "''", 'timetravel' : ?? } }

#        self.result # Sort of Error, When (timestamp)? Where (profile name)?, SQL itself, One or more (list) new ID-s or any other return values? 



        self.query_cols: list[DataColumn] | None = None 
        self.command_with_error: str = None
        self.profile_name: str = None
        self.last_run_datetime: datetime = None
        # last_error
        # last erroneous command
        # last time used
        # count of rows
        # name of profile (alias)

    def define(self, definition: dict):

        ...

    def prepare(self, values: dict | None = None) -> str:
        if not values: # eg {}
            self.command = self.sql_command_or_template
        else:
            try:
                self.command = generate_from_string(self.sql_command_or_template, values)
            except Exception as e1:
                self.command = ""
                logger.error(f"Error on using jinja2, check your SQL and parameter values")
        return self.command # if caller needs to reassure...


    def __str__(self) -> str:
        return self.command # built-command? list of build-commands?
    
    