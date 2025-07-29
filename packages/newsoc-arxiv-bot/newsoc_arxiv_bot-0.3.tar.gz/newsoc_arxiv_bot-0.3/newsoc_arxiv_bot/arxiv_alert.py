#!/usr/bin/env python3  

import argparse
import asyncio
import re
import sqlite3
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from telegram import Bot

# --- Config ---
TELEGRAM_TOKEN = "8181574175:AAEypktYxf4yHcC1SpOnxdnIdCGo0Xc_j2w"
TELEGRAM_CHAT_ID = 244431150
MIN_CITATIONS = 100  # Tweak for quality

class Paper(BaseModel):
    id: str
    title: str
    abstract: str
    published: str
    citations: int
    topic: str

def get_topic_db_name(topic: str) -> str:
    """Convert topic to valid filename"""
    return re.sub(r'\W+', '_', topic.lower()) + ".db"

def fetch_arxiv(topic: str) -> str:
    url = f"http://export.arxiv.org/api/query?search_query=all:{topic}+AND+cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

def parse_xml(xml: str, topic: str) -> List[Paper]:
    soup = BeautifulSoup(xml, "lxml-xml")
    papers = []
    
    for entry in soup.find_all("entry"):
        # Citation extraction
        citations = 0
        if comment := entry.find("arxiv:comment"):
            if match := re.search(r'\d+', comment.text):
                citations = int(match.group())

        # Skip low-impact papers
        if citations < MIN_CITATIONS:
            continue

        # Clean abstract
        abstract = entry.summary.text.strip()
        abstract = re.sub(r'\s+', ' ', abstract)  # Remove extra whitespace
        
        papers.append(Paper(
            id=entry.id.text.split("/")[-1],
            title=entry.title.text.strip(),
            abstract=abstract,
            published=entry.published.text,
            citations=citations,
            topic=topic
        ))
    
    return papers

def save_to_db(papers: List[Paper], db_file: str) -> List[Paper]:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            citations INTEGER,
            topic TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    new_papers = []
    for p in papers:
        if not c.execute("SELECT 1 FROM papers WHERE id=?", (p.id,)).fetchone():
            c.execute(
                "INSERT INTO papers (id, title, abstract, citations, topic) VALUES (?, ?, ?, ?, ?)",
                (p.id, p.title, p.abstract, p.citations, p.topic)
            )
            new_papers.append(p)
    
    conn.commit()
    conn.close()
    return new_papers

async def send_telegram_alert(papers: List[Paper]):
    bot = Bot(token=TELEGRAM_TOKEN)
    for p in papers:
        msg = (
            f"📄 *{p.topic.upper()}*\n"
            f"*{p.title}*\n\n"
            f"🔬 {p.citations} citations\n"
            f"📅 {p.published[:10]}\n\n"
            f"{p.abstract[:300]}{'...' if len(p.abstract) > 300 else ''}"
        )
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=msg,
            parse_mode="Markdown"
        )

async def main(topic: str):
    db_file = get_topic_db_name(topic)
    xml = fetch_arxiv(topic)
    papers = parse_xml(xml, topic)
    new_papers = save_to_db(papers, db_file)
    
    if new_papers:
        print(f"Found {len(new_papers)} new papers about {topic}")
        await send_telegram_alert(new_papers)
    else:
        print(f"No new papers found for {topic}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True, help="Research topic to search")
    args = parser.parse_args()
    
    asyncio.run(main(args.topic))
