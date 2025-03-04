import sqlite3
import pandas as pd

# Connect to the database
db_path = "data/movies.db"
conn = sqlite3.connect(db_path)

# Query the movies table
query = "SELECT * FROM movies;"
df = pd.read_sql_query(query, conn)

# Display the data
print(df)

# Save the data to an Excel file
excel_path = "movies_data.xlsx"
df.to_excel(excel_path, index=False)

print(f"Data saved to {excel_path}")

# Close the connection
conn.close()
