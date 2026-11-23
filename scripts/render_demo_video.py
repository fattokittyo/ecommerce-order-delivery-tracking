#!/usr/bin/env python3
"""Record a reproducible, narrated DBMS walkthrough from the actual local app.
Run in CI; generates Olist_DBMS_Demonstration_Video_GitHub.mp4 in the repo root.
"""
import csv
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
OUT = ROOT / "Olist_DBMS_Demonstration_Video_GitHub.mp4"
WORK = ROOT / ".demo_frames"
WORK.mkdir(exist_ok=True)

scenes = [
    ("Dashboard", "Welcome to our E-Commerce Order and Delivery Tracking System. "
     "We built this academic database prototype using a sample of thirty historical Olist orders. "
     "The dashboard displays twenty-eight delivered orders, five late deliveries, and two orders without a completed delivery date."),
    ("Order Search", "This screen displays order records from the local SQLite database. "
     "Orders are linked to their customer records by customer ID. "
     "We can search using an order identifier and immediately retrieve the matching purchase, shipment, and delivery dates."),
    ("Customer Records", "The customers table stores anonymized customer identifiers. "
     "Each order references a customer through a foreign key. "
     "The relationship demonstrates how primary keys and foreign keys help maintain database consistency."),
    ("Delivery Delays", "Our delivery report compares actual delivery dates with the estimated delivery dates. "
     "Orders delivered after their estimated date are marked late. "
     "In this small sample five of twenty-eight completed deliveries arrived late."),
    ("Delivery Follow-ups", "Administrators can record a follow-up note against an existing order. "
     "These follow-up records are new educational demonstration data. "
     "The original historical order records are left unchanged."),
    ("SQL Console", "The SQL console runs read-only SELECT queries against the SQLite database. "
     "Here we group orders by their recorded status to produce a summary. "
     "The repository also provides a separate MySQL script for coursework."),
    ("Database Schema", "Finally, the schema view displays relational tables, their columns and key relationships. "
     "This project applies DBMS concepts including primary keys, foreign keys, filtering, aggregation, and data analysis. "
     "Thank you for watching our demonstration.")
]

def run(args, **kwargs):
    print("+", " ".join(map(str,args)), flush=True)
    return subprocess.run(args, check=True, **kwargs)

def font(size, bold=False):
    base="/usr/share/fonts/truetype/dejavu/"
    filename="DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(base+filename, size)

def paragraph(draw, text, f, max_width):
    words=text.split()
    lines=[]
    cur=""
    for w in words:
        candidate=(cur+" "+w).strip()
        if draw.textbbox((0,0),candidate,font=f)[2] > max_width and cur:
            lines.append(cur)
            cur=w
        else:
            cur=candidate
    if cur:lines.append(cur)
    return lines

def add_caption(src, dst, title, words, number):
    im=Image.open(src).convert("RGB").resize((1280,720))
    overlay=Image.new("RGBA",(1280,720),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    d.rectangle((0,497,1280,720),fill=(12,36,54,240))
    d.text((40,518),f"{number:02d}  {title.upper()}",font=font(27,True),fill="white")
    sentences=words.split(". ")
    text=sentences[0].strip()
    if not text.endswith("."):text+="."
    lines=paragraph(d,text,font(22),1190)[:3]
    for k,line in enumerate(lines):
        d.text((40,574+32*k),line,font=font(22),fill=(224,244,248))
    im=Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB")
    im.save(dst,optimize=True)

with open(APP/"data/orders.csv",encoding="utf-8") as f:
    first=next(csv.DictReader(f))
order_id=first["order_id"]
proc=subprocess.Popen([sys.executable,"server.py"],cwd=APP,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
try:
    for i in range(50):
        try:
            with urlopen("http://127.0.0.1:8765/api/summary", timeout=2) as r:
                if r.status==200:break
        except Exception:time.sleep(0.25)
    else:raise RuntimeError("Local database app did not start")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1366,"height":768},device_scale_factor=1)
        page.goto("http://127.0.0.1:8765",wait_until="networkidle")
        actions=[
            lambda:None,
            lambda:(page.get_by_role("button",name="Orders",exact=True).click(), page.locator("#find").fill(order_id[:12])),
            lambda:page.get_by_role("button",name="Customers",exact=True).click(),
            lambda:page.get_by_role("button",name="Late Deliveries",exact=True).click(),
            lambda:(page.get_by_role("button",name="Follow-ups",exact=True).click(),
                    page.locator("#oid").fill(order_id),
                    page.locator("#note").fill("Check delivery confirmation with carrier"),
                    page.locator("#save").click()),
            lambda:(page.get_by_role("button",name="SQL Console",exact=True).click(),
                    page.locator("#sql").fill("SELECT order_status, COUNT(*) AS total FROM orders GROUP BY order_status"),
                    page.locator("#run").click()),
            lambda:page.get_by_role("button",name="Schema",exact=True).click()
        ]
        for i,(title,words) in enumerate(scenes,1):
            actions[i-1]()
            page.wait_for_timeout(500)
            shot=WORK/f"screen_{i}.png"
            page.screenshot(path=str(shot))
            add_caption(shot,WORK/f"frame_{i}.png",title,words,i)
        browser.close()
finally:
    proc.terminate()
    try:proc.wait(timeout=8)
    except subprocess.TimeoutExpired:proc.kill()

for i,(title,words) in enumerate(scenes,1):
    wav=WORK/f"voice_{i}.wav"
    run(["espeak","-s","135","-w",str(wav),words])
    duration=float(subprocess.check_output([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(wav)
    ]).decode().strip())+1.3
    run([
        "ffmpeg","-y","-loglevel","error","-loop","1","-framerate","12",
        "-i",str(WORK/f"frame_{i}.png"),"-i",str(wav),
        "-t",str(duration),"-vf","scale=1280:720",
        "-c:v","libx264","-preset","fast","-crf","27","-tune","stillimage",
        "-pix_fmt","yuv420p","-r","12","-c:a","aac","-b:a","80k",
        "-af","apad",str(WORK/f"clip_{i}.mp4")
    ])
concat=WORK/"concat.txt"
concat.write_text("".join(f"file '{WORK/f'clip_{i}.mp4'}'\n" for i in range(1,len(scenes)+1)))
run(["ffmpeg","-y","-loglevel","error","-safe","0","-f","concat","-i",
     str(concat),"-c","copy",str(OUT)])
print(f"Created {OUT} ({OUT.stat().st_size} bytes)",flush=True)
