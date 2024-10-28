import sqlite3
import csv


def export_table_to_csv(db_path, table_name, csv_file_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")

    columns = [description[0] for description in cursor.description]

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)
        writer.writerows(cursor.fetchall())

    conn.close()


db_path = 'site.db'
export_table_to_csv(db_path, 'Subreddit', 'Subreddit.csv')
export_table_to_csv(db_path, 'Post', 'Post.csv')
export_table_to_csv(db_path, 'Response', 'Response.csv')

print("Export finished!")
