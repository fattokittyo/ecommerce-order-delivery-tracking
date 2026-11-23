# E-Commerce Order and Delivery Tracking System

A DBMS case study prototype for **B.E. Computer Science and Engineering, III Semester (2026–2027)** at Stanley College of Engineering & Technology for Women, Hyderabad.

**Student team:** Ridah Ahmed (160625733054), Madiha Fatima (160625733039), and Manza Fatima Injila (160625733041).

## Overview
This project demonstrates order tracking, delivery-date analysis, SQL relationships, and follow-up records using a small **30-order excerpt of historical anonymized Olist e-commerce data**. The excerpt contains 28 delivered orders, including 5 deliveries after the estimated date, and 2 orders without a delivered date. These figures describe **this excerpt only**, not the entire Olist dataset.

**Dataset:** Brazilian E-Commerce Public Dataset by Olist — https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

This is an educational prototype and **is not affiliated with or operated by Olist**. It does not process live orders or contain verified customer names or addresses.

## Two different demonstrations

1. **Public static dashboard (GitHub Pages):** `index.html` — opens in any browser; shows the embedded historical sample, search, filters and delivery-rate overview. **It is not connected to a live SQL database.**
2. **Local working database app:** `app/` — includes a Python standard-library web server, SQLite database and HTML frontend. It supports live read-only SQL queries, relational tables and adding/resolving locally created follow-up records. The ZIP also contains a separate **MySQL 8 schema and sample-data script** for the database course. The live web app uses SQLite, not MySQL.

## Run the interactive local app

1. Download `app/` and extract it on a computer.
2. Install Python 3 if necessary. No `pip` packages are required.
3. On Windows, double-click `start_windows.bat`; on macOS/Linux, run `python3 server.py` from the extracted folder.
4. Visit `http://127.0.0.1:8765` in your browser.
5. Explore **Dashboard → Orders → Customers → Delivery Delays → Follow-ups → SQL Console → Schema**.

The local app is intended for a classroom demonstration; **do not expose its HTTP server to the public internet**. The Follow-ups table contains new demonstration notes, separate from Olist data.

## Files

| File | Description |
| --- | --- |
| `index.html` | Standalone static, GitHub Pages-compatible dashboard (no server) |
| `app/` | Full Python + SQLite interactive DBMS app and MySQL 8 script |
| `mysql_schema_and_sample.sql` | Standalone MySQL 8 schema and sample SQL |
| `orders_sample.csv` | 30 historical Olist order rows used for the demonstration |
| `customers_sample.csv` | Linked customer ID excerpt; unverified customer metadata remains blank |
| `Olist_DBMS_Demonstration_Video.mp4` | Two-minute walkthrough of the local database app |

## Video

[Watch or download the project walkthrough](Olist_DBMS_Demonstration_Video.mp4)

## GitHub Pages setup

After uploading these files to a public GitHub repository, go to **Settings → Pages → Build and deployment → Deploy from a branch**, select branch **main**, folder **/(root)**, and save. The published link will be `https://fattokittyo.github.io/ecommerce-order-delivery-tracking/` once GitHub completes deployment. This link hosts only the static `index.html` demo, not the Python + SQLite backend.

## Academic integrity note

This repository contains educational sample software and a public historical dataset excerpt. No claim is made that the system has been deployed for an actual business. Report screenshots and test outcomes should be based on the code run by the students.