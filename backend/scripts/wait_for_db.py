import socket, os, time
host=os.getenv('POSTGRES_HOST','postgres'); port=int(os.getenv('POSTGRES_PORT','5432'))
for _ in range(60):
    try: socket.create_connection((host,port),2).close(); raise SystemExit(0)
    except OSError: time.sleep(1)
raise SystemExit(1)
