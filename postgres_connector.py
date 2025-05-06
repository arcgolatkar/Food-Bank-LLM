# import psycopg2
# import psycopg2.extras


def connect_to_postgres(db_host, db_name, db_user, db_password, db_port, llm1_output):

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    
    # Create a cursor and execute the query
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        # Create SQL query to filter data
        sql_command = f"""
        SELECT * FROM data
        WHERE REGION = %s
        AND COUNTY = %s
        """
        
        # Execute the query with parameters (safer than string formatting)
        cursor.execute(sql_command, (llm1_output['region'], llm1_output['county']))
        
        # Fetch results
        rows = cursor.fetchall()
        filtered_df = [dict(row) for row in rows]
        
        # Close the connection
        conn.close()

    return filtered_df