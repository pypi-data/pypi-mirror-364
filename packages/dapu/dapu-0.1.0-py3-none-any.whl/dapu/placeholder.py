from enum import Enum

class Placeholder(Enum):
    """
    What are generally allowed placehodlers in text files or sql-strings 
    """
    TARGET_SCHEMA: str = '{{target_schema}}'
    TARGET_TABLE: str = '{{target_table}}'
    TARGET_TABLE_SHADOW: str = '{{target_table_shadow}}'
    TARGET_KEY_COLUMNS: str = '{{key_columns}}'
    TARGET_DATA_COLUMNS: str = '{{data_columns}}'
    LAST_VALUE_TS: str = '{{last_ts_value}}'
    SOURCE_COLUMN_TS: str = '{{ts_column}}'
    SOURCE_COUNT_SKIP: str = '{{skip_count}}' # aka OFFSET, human interpretable ("skip 3" means "start from 4th")
    SOURCE_COUNT_LIMIT: str= '{{limit_count}}'
    