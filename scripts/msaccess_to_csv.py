import csv
import pyodbc
import sys


def main(db_path, output):
    conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_path)
    cur = conn.cursor()
    data = cur.execute('select * from members').fetchall()
    columns = [r[0] for r in cur.description]
    data = [columns] + data
    with open(output, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: {0} db output".format(sys.argv[0]))
    else:
        main(*sys.argv[1:])
