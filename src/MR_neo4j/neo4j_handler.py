# Neo4j图数据库驱动
import neo4j

NEO4J_URI = "bolt://123.207.15.126:7687"
NEO4J_AUTH = ("neo4j", "Microrust")

def clean_all_files():
    """清除Neo4j数据库中的所有文件和标签"""

    driver = None # 预先定义

    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth = NEO4J_AUTH)
        with driver.session() as session:
            # 删除所有节点及其关系
            session.run("MATCH (n) DETACH DELETE n")  
    
    except Exception as e:
        return f"Neo4j ERROR: {str(e)}"
    
    finally:
        if driver is not None:
            driver.close() # 检查driver是否存在

def add_new_file(cid: str, filename: str, tags: list[str]):
    """向Neo4j数据库中的添加文件和标签"""
    
    driver = None
    
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth = NEO4J_AUTH)
        with driver.session() as session:
            # 更新Neo4j数据库, cid, filename和文件视为点, tag视为点, 关联关系视为边
            session.run(
                "MERGE (f:File {cid: $cid}) "
                "SET f.filename = $filename", # 使用SET更新filename属性
                cid=cid, filename=filename
            )
            
            for tag in tags:
                session.run(
                    "MERGE (t:Tag {name: $tag})", # 用MERGE, 避免重复插入
                    tag=tag
                )
                session.run(
                    "MATCH (f:File {cid: $cid}), (t:Tag {name: $tag}) "
                    "MERGE (f)-[:TAGGED_WITH]->(t)",
                    cid=cid, tag=tag
                )
    
    except Exception as e:
        return f"Neo4j ERROR: {str(e)}"
    
    finally:
        if driver is not None:
            driver.close()

def delete_file_by_cid(cid: str):
    """删除指定cid的文件"""
    
    driver = None
    
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth = NEO4J_AUTH)
        with driver.session() as session:
            session.run(
                "MATCH (f:File {cid: $cid}) DETACH DELETE f",
                cid=cid
            )
    
    except Exception as e:
        return f"Neo4j ERROR: {str(e)}"
    
    finally:
        if driver is not None:
            driver.close()

def delete_file_by_filename(filename: str):
    """删除指定filename的文件"""
    
    driver = None
    
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth = NEO4J_AUTH)
        with driver.session() as session:
            session.run(
                "MATCH (f:File {filename: $filename}) DETACH DELETE f",
                filename=filename
            )
    
    except Exception as e:
        return f"Neo4j ERROR: {str(e)}"
    
    finally:
        if driver is not None:
            driver.close()

def query_files_by_tags(tags: list[str], limit: int) -> list:
    """
    根据标签查询文件,
    输入: tags: 标签列表 
          limit: 希望返回的匹配度最高的文件个数, 如果匹配至少一个标签的文件数量不足limit, 则返回所有匹配至少一个标签的文件
    输出: 文件列表, 列表中的每个元素为一个字典, 包含filename, cid和tags项
    
    例子：
        输入: tags = ["geography", "mountains"], limit = 2
        输出: [
            {"filename": "example1.txt", "cid": "123", "tags": ["geography", "mountains", "txt"]},
            {"filename": "example2.pdf", "cid": "456", "tags": ["geography", "pdf"]}
        ]
    """
    
    driver = None
    
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth = NEO4J_AUTH)
        with driver.session() as session:
            # 使用UNWIND将tags列表展开为多个行进行匹配
            result = session.run(
                "MATCH (f:File)-[:TAGGED_WITH]->(t:Tag) "
                "WHERE t.name IN $tags "
                "RETURN f.filename AS filename, f.cid AS cid, collect(t.name) AS tags "
                "ORDER BY size(tags) DESC "
                "LIMIT $limit",
                tags=tags,
                limit=limit
            )
            result_cids = [record["cid"] for record in result]
            
            # 获得这些cid对应的filename和tags
            final_result = []
            for cid in result_cids:
                file_result = session.run(
                    "MATCH (f:File {cid: $cid}) "
                    "OPTIONAL MATCH (f)-[:TAGGED_WITH]->(t:Tag) "
                    "RETURN f.filename AS filename, f.cid AS cid, collect(t.name) AS tags",
                    cid=cid
                )

                for record in file_result:
                    final_result.append({
                        "filename": record["filename"],
                        "cid": record["cid"],
                        "tags": record["tags"]
                    })
            return final_result
    
    except Exception as e:
        return [f"Neo4j ERROR: {str(e)}"]
    
    finally:
        if driver is not None:
            driver.close()

def query_files_by_filename(filename: str) -> list:
    """
    根据文件名查询文件,
    输入: filename: 文件名
    输出: 所有名为指定文件名的文件列表, 列表中的每个元素为一个字典, 包含filename, cid和tags项

    例子：
        输入 filename = "example.txt"
        输出 [
            {"filename": "example.txt", "cid": "123", "tags": ["geography", "mountains", "txt"]}
            {"filename": "example.txt", "cid": "456", "tags": ["geography", "rivers", "txt"]}
        ]
    """
    
    driver = None
    
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        with driver.session() as session:
            result = session.run(
                "MATCH (f:File {filename: $filename}) "
                "OPTIONAL MATCH (f)-[:TAGGED_WITH]->(t:Tag) "
                "RETURN f.filename AS filename, f.cid AS cid, collect(t.name) AS tags",
                filename=filename
            )
            return [{"filename": record["filename"], "cid": record["cid"], "tags": record["tags"]} for record in result]
    
    except Exception as e:
        return [f"Neo4j ERROR: {str(e)}"]
    
    finally:
        if driver is not None:
            driver.close()

# 测试代码
if __name__ == "__main__":
    clean_all_files()
    
    cid = "example_cid"
    filename = "example.txt"
    tags = ["geography", "mountains", "world", "txt"]
    
    add_new_file(cid, filename, tags)
    
    result = query_files_by_tags(["geography", "mountains"], 2)
    print("查询结果(tag):", result)
    
    result = query_files_by_filename("example.txt")
    print("查询结果(filename):", result)
    
    print("Neo4j数据库更新成功!")