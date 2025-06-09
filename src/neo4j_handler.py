import neo4j

NEO4J_URI = "bolt://117.68.10.96:27734"
NEO4J_AUTH = ("neo4j", "Microrust")

def clean_all_files() -> None:
    """清除Neo4j数据库中的所有文件和标签"""
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")  # 删除所有节点及其关系
    except Exception as e:
        return f"❌ Neo4j ERROR: {str(e)}"
    finally:
        driver.close()

def add_new_file(cid: str, filename: str, tags: list[str]) -> None:
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        with driver.session() as session:
            # 更新Neo4j数据库, 文件和 cid、filename 视为点，tag 视为点，关联关系视为边
            session.run(
                "MERGE (f:File {cid: $cid}) "
                "SET f.filename = $filename",  # 使用 SET 更新 filename 属性
                cid=cid, filename=filename
            )
            for tag in tags:
                session.run(
                    "MERGE (t:Tag {name: $tag})",  # 用 MERGE，避免重复插入
                    tag=tag
                )
                session.run(
                    "MATCH (f:File {cid: $cid}), (t:Tag {name: $tag}) "
                    "MERGE (f)-[:TAGGED_WITH]->(t)",
                    cid=cid, tag=tag
                )
    except Exception as e:
        return f"❌ Neo4j ERROR: {str(e)}"
    finally:
        driver.close()

def delete_file_by_cid(cid: str) -> None:
    """
    删除指定 cid 的文件
    """
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        with driver.session() as session:
            session.run(
                "MATCH (f:File {cid: $cid}) DETACH DELETE f",
                cid=cid
            )
    except Exception as e:
        return f"❌ Neo4j ERROR: {str(e)}"
    finally:
        driver.close()

def delete_file_by_filename(filename: str) -> None:
    """
    删除指定 filename 的文件
    """
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        with driver.session() as session:
            session.run(
                "MATCH (f:File {filename: $filename}) DETACH DELETE f",
                filename=filename
            )
    except Exception as e:
        return f"❌ Neo4j ERROR: {str(e)}"
    finally:
        driver.close()
    

def query_files_by_tags(tags: list[str], limit: int) -> list:
    """
    根据标签查询文件,
    输入: tags : 标签列表 limit : 希望返回的匹配度最高的文件个数
    输出: 文件列表，列表中的每个元素为一个字典，包含 filename, cid 和 tags 项

    例子：
        输入 tags = ["geography", "mountains"], limit = 2
        输出 [
            {"filename": "example1.txt", "cid": "123", "tags": ["geography", "mountains", "txt"]},
            {"filename": "example2.pdf", "cid": "456", "tags": ["geography", "pdf"]}
        ]
    """
    raise NotImplementedError("查询功能尚未实现")


if __name__ == "__main__":
    # 测试代码
    clean_all_files()
    
    cid = "example_cid"
    filename = "example.txt"
    tags = ["geography", "mountains", "world", "txt"]
    
    add_new_file(cid, filename, tags)
    print("Neo4j 数据库更新成功！")
