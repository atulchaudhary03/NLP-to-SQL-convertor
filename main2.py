from dotenv import load_dotenv
import os
import sqlite3
import google.generativeai as genai
import streamlit as st

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
DATABASE_PATH = r'C:\Users\monuc\OneDrive\Desktop\NLP to SQL Project'

def get_google_gemini(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt, question])
        return response.text.strip()
    except Exception as e:
        print(f"Error in Google Gemini API call: {e}")
        return ""

def sql_query(sql, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("Executing SQL:", sql)  
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
        return []

def create_database_and_table(db_name, table_name, columns):
    try:
        db_path = os.path.join(DATABASE_PATH, f'{db_name}.db')
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        column_defs = ', '.join([f'"{col.strip()}" TEXT' for col in columns])
        table_info = f"""
        CREATE TABLE IF NOT EXISTS "{table_name.strip()}" (
            {column_defs}
        );
        """
        print("Executing SQL:", table_info)  
        cursor.execute(table_info)
        connection.commit()
        st.success(f"Database '{db_name}' and table '{table_name}' with columns {columns} have been created.")
    except sqlite3.OperationalError as e:
        st.error(f"OperationalError: {e}")
        print(f"OperationalError: {e}")
    finally:
        connection.close()

def insert_into_table(db_name, table_name, values):
    try:
        db_path = os.path.join(DATABASE_PATH, f'{db_name}.db')
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # sql insert statement
        placeholders = ', '.join(['?' for _ in values])
        insert_query = f"INSERT INTO \"{table_name}\" VALUES ({placeholders})"
        print("Executing SQL:", insert_query)  
        cursor.execute(insert_query, values)
        connection.commit()
        st.success(f"Data {values} has been inserted into table '{table_name}'.")
    except sqlite3.OperationalError as e:
        st.error(f"OperationalError: {e}")
        print(f"OperationalError: {e}")
    finally:
        connection.close()


prompts = [
    """
    
     You are an expert in converting English questions to SQL queries!
     The SQL database has a table named STUDENT with various columns.
     The SQL code should not have ''' in the beginning or end, and the word SQL should not appear in the output.
     The SQL code should not have 'The'in the output.
     The SQL queries should not be written the first letter in capital and all will be written in small letters.
     The SQL queries should not add 's' in the table name in the output.

     For example:

      Example 1 - How many students are there?
      The SQL command will be something like this: SELECT COUNT(*) FROM STUDENT;

     Example 2 - List all students.
      The SQL command will be something like this: SELECT * FROM STUDENT;

      Example 3 - Show the names and marks of all students.
       The SQL command will be something like this: SELECT NAME, MARKS FROM STUDENT;

     Example 4 - Find the average marks in each class.
     The SQL command will be something like this: SELECT CLASS, AVG(MARKS) FROM STUDENT GROUP BY CLASS;

     Example 5 - What is the highest mark scored by any student?
     The SQL command will be something like this: SELECT MAX(MARKS) FROM STUDENT;

      Example 6 - List students whose names start with 'A'.
     The SQL command will be something like this: SELECT * FROM STUDENT WHERE NAME LIKE 'A%';

     Example 7 - Find students who scored between 70 and 90 marks.
     The SQL command will be something like this: SELECT * FROM STUDENT WHERE MARKS BETWEEN 70 AND 90;

      Example 8 - List all students ordered by their marks in descending order.
      The SQL command will be something like this: SELECT * FROM STUDENT ORDER BY MARKS DESC;

      Example 9-how many books are there of dsa in library.
      The SQL command will be something like this: SELECT COUNT(*) FROM library WHERE books= "dsa";

      Example 10 - how many books have quantity more than 50.
      The SQL command will be something like this: SELECT COUNT(*) FROM books WHERE quantity>50;

      Example 11 - tell me the ref of book named automera in library
      The SQL command will be something like this: select ref from library where books="automera";

      

      """
]


st.set_page_config(page_title="Gemini SQL Query Retriever")
st.header("Gemini App to Retrieve Data")


db_name = st.text_input("Enter database name:", key="db_name")
table_name = st.text_input("Enter table name:", key="table_name")
columns_input = st.text_input("Enter columns (comma-separated):", key="columns_input")
create_data = st.button("Create Database and Table")

if create_data and db_name and table_name and columns_input:
    columns = [col.strip() for col in columns_input.split(',')]
    create_database_and_table(db_name, table_name, columns)

#data insert
values_input = st.text_area("Enter values to insert (comma-separated):", key="values_input")
insert_data = st.button("Insert Data")

if insert_data and values_input and db_name and table_name:
    values = [val.strip() for val in values_input.split(',')]
    insert_into_table(db_name, table_name, values)


question = st.text_input("Input your query here:", key="query")
submit = st.button("Ask the Question")

if submit and question:
    response = get_google_gemini(question, prompts[0])
    if response:
        print("Generated SQL:", response)  
        db_path = os.path.join(DATABASE_PATH, f"{db_name}.db")
        data = sql_query(response, db_path)
        st.subheader("The response is:")
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("No data found or an error occurred.")
    else:
        st.write("Failed to generate SQL query from the given question.")