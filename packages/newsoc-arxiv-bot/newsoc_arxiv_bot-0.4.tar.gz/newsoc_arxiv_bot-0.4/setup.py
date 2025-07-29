from setuptools import setup  

setup(  
    name="newsoc-arxiv-bot",  
    version="0.4",  
    packages=["newsoc_arxiv_bot"],  
    entry_points={"console_scripts": ["arxiv-bot=newsoc_arxiv_bot.arxiv_alert:main"]},  
    install_requires=["requests", "python-telegram-bot", "pydantic", "beautifulsoup4", "lxml"]  
)  
