"""
Utility functions for database work
"""

import sqlalchemy as db

def change_schema(metadata: db.MetaData, schema: str) -> db.MetaData:
    """
    Change the schema of a metadata object and all its child tables for testing purposes

    Args:
        metadata: db.MetaData object to work on
        schema: new schema name

    Returns:
        db.MetaData: new metadata object
    """
    old_schema = metadata.schema
    metadata.schema = schema

    new_tables = dict()

    for table_name, table in metadata.tables.items():
        new_table_name = table_name.replace(old_schema, schema)
        table.schema = schema
        new_tables[new_table_name] = table

    metadata.tables = new_tables
    return metadata

