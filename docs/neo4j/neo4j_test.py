from neo4j import GraphDatabase

URI = "bolt://117.68.10.96:27734"
AUTH = ("neo4j", "Microrust")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

    with driver.session() as session:
        # 插入一些 Person 节点（如果之前已经插入过，这里可以跳过）
        people = ["Alice", "Bob", "Charlie", "Diana"]
        for name in people:
            session.run(
                "MERGE (p:Person {name: $name})",  # 用 MERGE，避免重复插入
                name=name
            )
        print("Nodes inserted.")

        # 插入一些关系：KNOWS
        relationships = [
            ("Alice", "Bob"),
            ("Bob", "Charlie"),
            ("Charlie", "Diana")
        ]
        for person1, person2 in relationships:
            session.run(
                """
                MATCH (a:Person {name: $person1})
                MATCH (b:Person {name: $person2})
                MERGE (a)-[:KNOWS]->(b)
                """,
                person1=person1,
                person2=person2
            )
        print("Relationships created.")

        # 查询并打印所有 Person 节点及他们认识的人
        result = session.run(
            """
            MATCH (a:Person)-[:KNOWS]->(b:Person)
            RETURN a.name AS from, b.name AS to
            """
        )
        print("Relationships in database:")
        for record in result:
            print(f"{record['from']} KNOWS {record['to']}")
