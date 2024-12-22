import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(verbose=True)

driver = GraphDatabase.driver(
   os.environ['NEO4J_URI'],
   auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'])
)