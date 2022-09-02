def create_insert_statement_for_table(table):
    column_names = ", ".join(table.c.keys())
    insert_stmt = f"INSERT INTO {table.name} ({column_names}) VALUES"
    return insert_stmt

