from neo4j import GraphDatabase


def connect():
    driver = GraphDatabase.driver(uri='bolt://localhost:7687', auth=('neo4j', '4321'))
    session = driver.session()
    return session
