from loguru import logger
from typing import Any
"""
from _typeshed.dbapi import DBAPIConnection, DBAPICursor
import typehelper
import typing
AConnection = typing.TypeVar("AConnection", typehelper.DBAPIConnection, None)
ACursor = typing.TypeVar("ACursor", typehelper.DBAPICursor, None)
"""

"""
import psycopg
import mariadb
import typing
AConnection = typing.TypeVar("AConnection", DBAPIConnection, psycopg.Connection)
con1: psycopg.Connection = psycopg.connect()
con2: DBAPIConnection = mariadb.connect()
con3: AConnection = psycopg.connect()
con4: AConnection = mariadb.connect()
con5: DBAPIConnection | psycopg.Connection = psycopg.connect()
con6: DBAPIConnection | psycopg.Connection = mariadb.connect()
"""

class MyCursor():
    arraysize = 10 # missing attribute in DBAPICursor

class DummyCursor(MyCursor):
    def __init__(self) -> None:
        self.counter = 0
        self.sample_data: list[tuple] = [(4, "Marju"), (5, "Liina"), (1, "Juta"), (23, "Mai"), (4, "Marju")]

    def close(self):
        self.counter = 0
        
    def fetchone(self) -> tuple | None:
        if self.counter < len(self.sample_data):
            self.counter += 1
            return self.sample_data[self.counter -1]
        else:
            return None
   
    def fetchall(self, size=MyCursor.arraysize) -> list[tuple]:
        return self.sample_data
        
class DataRowTuple():
    """
    Safe code shortener. DataCapsule dc[0][0] will work if dc[0] is DataRowTuple (and will not work if dc[0] is None)
    """
    def __init__(self, row: tuple|None = None) -> None:
        if row is None:
            self.data: tuple = (None,)
            self.empty = False
        else:
            self.data: tuple = row
            self.empty = True

    # iterator stuff (everything is loaded into memory, into list)
    def __iter__(self):
        self.position = 0
        return self
    
    def __len__(self):
        return len(self.data)

    def __next__(self):
        if self.empty:
            raise StopIteration
        try:
            result = self.data[self.position]
            self.position += 1
        except IndexError:
            raise StopIteration
        return result
    
    def __getitem__(self, index) -> Any:
        try:
            return self.data[index]
        except IndexError:
            return None
    
    def row_exists(self) -> bool:
        return not self.empty
    

class DataCapsule():
    """
    Demand for SQL command and its result
    """
    def __init__(self, sql: str | None = None) -> None:
        # command
        self.sql_command: str = sql if sql else ""
        # behaviour
        self.do_return: bool | None = True
        # result
        self.result_set = []
        self.open_cursor: None | DummyCursor = None
        # statistics
        self.last_profile_name: str = ""
        self.last_consumed_time: float = 0.00
        self.last_error_message: str = ""
        self.last_action_success: bool | None = None

    def __str__(self) -> str:
        return self.sql_command

    # iterator stuff (everything is loaded into memory, into list)
    def __iter__(self):
        self.position = 0
        return self
    
    def __len__(self):
        return len(self.result_set)

    def __next__(self):
        try:
            result = self.result_set[self.position]
            self.position += 1
        except IndexError:
            raise StopIteration
        return result

    # magically asking by index using []
    def __getitem__(self, index) -> DataRowTuple:
        try:
            return DataRowTuple(self.result_set[index])
        except IndexError:
            return DataRowTuple(None)
    
    # non-magically asking by two indexes ( , )
    def getitem(self, row_index, col_index, on_error_return = None) -> Any:
        try:
            return DataRowTuple(self.result_set[row_index])[col_index]
        except IndexError:
            return on_error_return
    
    def row_exists(self, row_index) -> bool:
        if row_index >= 0:
            if len(self.result_set) > row_index and self[row_index].row_exists():
                return True
        else:
            if len(self.result_set) >= abs(row_index) and self[row_index].row_exists():
                return True
        return False
        

    # fetching one by one
    def stream(self, keep: bool = False):
        if self.open_cursor and hasattr(self.open_cursor, "fetchone"):
            while True:
                row: tuple | None = self.open_cursor.fetchone()
                if row is None:
                    break
                if keep:
                    self.result_set.append(row)
                yield row
            self.close_stream()

    # assignment stuff
    def set_command(self, sql_command: str):
        self.sql_command = sql_command

    def set_return(self, do_return: bool):
        self.do_return = do_return

    def set_action_data_profile(self, profile_name: str):
        self.last_profile_name = profile_name
    
    def set_action_consumed_time(self, seconds: float):
        self.last_consumed_time = seconds

    def set_action_error(self, error_message: str):
        self.last_error_message = error_message
        if error_message:
            self.last_action_success = False
        else:
            self.last_action_success = True

    def set_action_success(self, success: bool):
        self.last_action_success = success
        if success:
            self.last_error_message = ""

    def open_stream(self, cursor): # anname kursori, mida saab kirjehaaval lugeda
        self.open_cursor = cursor
        self.result_set = []

    def close_stream(self):
        if self.open_cursor and hasattr(self.open_cursor, "close"):
            self.open_cursor.close()
        self.open_cursor = None

    def load_data(self, cursor): # anname avatud kursori, mis loetakse korraga sisse (numbriline index)
        self.result_set = []
        self.close_stream() # if opened
        if self.do_return and cursor and hasattr(cursor, "fetchall"):
            try:
                self.result_set = cursor.fetchall()
            except Exception as e1:
                logger.warning(f"Nothing to fetch (ok, if guessing) {e1}")

    def import_yaml_list(self, yaml_list_string: str):
        ...

    # 
    def test_add(self, something: str):
        self.result_set.append(something)

def enname(row: tuple[Any, ...], declaration: dict[int, str]|list[str|None]) -> dict:
    record: dict = {}
    if isinstance(declaration, list):
        for pos, item in enumerate(declaration, 0):
            if item is not None and pos < len(row):
                record[item] = row[pos]
    elif isinstance(declaration, dict):
        for key, value in declaration.items():
            if key is not None and key < len(row) and value is not None:
                record[value] = row[key]
    return record
    
def test():
    dc = DataCapsule()
    names: list[str | None] = ["id", "name"]
    #names: dict[int, str] = {0: "id", 1: "name", 2: "muu"}
    
    dc.open_stream(DummyCursor())
    for row in dc.stream(True):
        print(enname(row, names))
    dc.load_data(DummyCursor())

    for row in dc:
        print(row)

if __name__ == '__main__':
    test()
