import sqlite3
conn = sqlite3.connect('knowledge_base.db')
c = conn.cursor()
c.execute("SELECT DISTINCT section FROM faq WHERE section LIKE '%program%' OR section LIKE '%diploma%' OR section LIKE '%course%' ORDER BY section ASC;")
results = c.fetchall()
print(f'Programs/diplomas/courses: {len(results)}')
for row in results:
    print(row[0])
conn.close()
