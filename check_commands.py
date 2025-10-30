import sqlite3

# Connect to the database
conn = sqlite3.connect('adms.db')
cursor = conn.cursor()

# Check for queued commands
cursor.execute("SELECT * FROM device_commands WHERE status = 'queued'")
queued_commands = cursor.fetchall()
print("Queued Commands:")
for command in queued_commands:
    print(command)

# Check for sent commands
cursor.execute("SELECT * FROM device_commands WHERE status = 'sent'")
sent_commands = cursor.fetchall()
print("\nSent Commands:")
for command in sent_commands:
    print(command)

# Check for completed commands
cursor.execute("SELECT * FROM device_commands WHERE status = 'completed'")
completed_commands = cursor.fetchall()
print("\nCompleted Commands:")
for command in completed_commands:
    print(command)

conn.close()