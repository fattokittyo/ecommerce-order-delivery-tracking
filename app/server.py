"""Educational Olist DBMS demo: Python standard library + SQLite. Local use only."""
import csv, json, sqlite3, pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
ROOT=pathlib.Path(__file__).resolve().parent
DB=ROOT/"demo.sqlite3"
def con():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON");return c
def init():
 with con() as c:
  c.executescript("""
  CREATE TABLE IF NOT EXISTS customers(customer_id TEXT PRIMARY KEY,customer_unique_id TEXT,customer_zip_code_prefix TEXT,customer_city TEXT,customer_state TEXT);
  CREATE TABLE IF NOT EXISTS orders(order_id TEXT PRIMARY KEY,customer_id TEXT NOT NULL REFERENCES customers(customer_id),order_status TEXT,order_purchase_timestamp TEXT,order_approved_at TEXT,order_delivered_carrier_date TEXT,order_delivered_customer_date TEXT,order_estimated_delivery_date TEXT);
  CREATE TABLE IF NOT EXISTS followups(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id TEXT NOT NULL REFERENCES orders(order_id),note TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Open');
  CREATE VIEW IF NOT EXISTS delivery_report AS SELECT o.order_id,o.customer_id,o.order_status,substr(o.order_purchase_timestamp,1,10) purchased,substr(o.order_delivered_customer_date,1,10) delivered,substr(o.order_estimated_delivery_date,1,10) estimated,CASE WHEN o.order_delivered_customer_date IS NULL THEN 'Not delivered' WHEN date(o.order_delivered_customer_date)>date(o.order_estimated_delivery_date) THEN 'Late' ELSE 'On time' END result FROM orders o;
  """)
  if not c.execute("SELECT count(*) FROM orders").fetchone()[0]:
   for table in ["customers","orders"]:
    with open(ROOT/"data"/(table+".csv"),encoding="utf-8-sig",newline="") as f:
     reader=csv.DictReader(f);cols=reader.fieldnames
     c.executemany("INSERT INTO "+table+"("+",".join(cols)+") VALUES("+",".join(["?"]*len(cols))+")",[[row[x] or None for x in cols] for row in reader])
def query(sql,params=()):
 with con() as c:return [dict(x) for x in c.execute(sql,params).fetchall()]
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,obj,status=200):
  b=json.dumps(obj).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  url=urlparse(self.path);p=url.path
  if p in ["/","/index.html"]:
   b=(ROOT/"index.html").read_bytes();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);return
  try:
   if p=="/api/orders":
    q=parse_qs(url.query).get("q",[""])[0];return self.send(query("SELECT * FROM delivery_report WHERE order_id LIKE ? OR customer_id LIKE ? ORDER BY purchased DESC",("%"+q+"%","%"+q+"%")))
   if p=="/api/customers":return self.send(query("SELECT c.customer_id,c.customer_city,c.customer_state,count(o.order_id) orders FROM customers c LEFT JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id"))
   if p=="/api/late":return self.send(query("SELECT * FROM delivery_report WHERE result='Late'"))
   if p=="/api/followups":return self.send(query("SELECT * FROM followups ORDER BY id DESC"))
   if p=="/api/schema":return self.send(query("SELECT name,type,sql FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'"))
   if p=="/api/summary":return self.send(query("SELECT count(*) total,sum(result='Late') late,sum(result='On time') on_time,sum(result='Not delivered') pending FROM delivery_report")[0])
   self.send({"error":"Not found"},404)
  except Exception as e:self.send({"error":str(e)},500)
 def do_POST(self):
  try:
   obj=json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))) or "{}");p=urlparse(self.path).path
   if p=="/api/sql":
    sql=str(obj.get("query","")).strip().rstrip(";")
    if not sql.lower().startswith(("select ","with ")) or ";" in sql or len(sql)>2000:return self.send({"error":"Only single read-only SELECT queries allowed"},400)
    with con() as c:
     c.execute("PRAGMA query_only=ON");cur=c.execute(sql);names=[x[0] for x in cur.description];records=[dict(zip(names,x)) for x in cur.fetchmany(100)]
    return self.send(records)
   if p=="/api/followups":
    order=str(obj.get("order_id",""));note=str(obj.get("note","")).strip()[:300]
    if not note:return self.send({"error":"Please enter a note"},400)
    with con() as c:c.execute("INSERT INTO followups(order_id,note) VALUES(?,?)",(order,note))
    return self.send({"saved":True})
   if p=="/api/resolve":
    with con() as c:c.execute("UPDATE followups SET status='Resolved' WHERE id=?",(int(obj["id"]),))
    return self.send({"saved":True})
   self.send({"error":"Not found"},404)
  except Exception as e:self.send({"error":str(e)},400)
if __name__=="__main__":
 init();print("Open http://127.0.0.1:8765");ThreadingHTTPServer(("127.0.0.1",8765),Handler).serve_forever()
