from fastapi import FastAPI, Depends, APIRouter, HTTPException
from auth import verify_token
from models import UserModel, GroupModel, NodeRelationships
from database import driver

router = APIRouter()

# Получение всех узлов с атрибутами
@router.get("/nodes/")
def get_all_nodes():
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN n")
            nodes = [record["n"] for record in result]
        return {"nodes": [dict(node) for node in nodes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Получение узла и его связей
@router.get("/nodes/{node_id}")
def get_node_with_relationships(node_id: int):
    with driver.session() as session:
        query = """
        MATCH (u:User {id: $node_id})
        OPTIONAL MATCH (u)-[:Follow]->(f:User)
        OPTIONAL MATCH (u)-[:Subscribe]->(g:Group)
        RETURN u, COLLECT(f) as follows, COLLECT(g) as subscribes
        """
        result = session.run(query, node_id=node_id).single()
        if not result or not result["u"]:
            raise HTTPException(status_code=404, detail="Node not found")

        # Извлекаем узел пользователя и связи
        user = result["u"]
        follows = result["follows"]
        subscribes = result["subscribes"]

        # Приводим данные к словарю, обрабатывая отсутствие полей
        def clean_data(record):
            return {key: record[key] for key in record.keys()}

        return NodeRelationships(
            node=UserModel(**clean_data(user)),
            follows=[UserModel(**clean_data(f)) for f in follows],
            subscribes=[GroupModel(**clean_data(g)) for g in subscribes]
        )


# Добавление узла (с защитой токена)
@router.post("/nodes/", dependencies=[Depends(verify_token)])
def add_node(user: UserModel):
    with driver.session() as session:
        query = """
        MERGE (u:User {id: $id})
        SET u.name = $name, u.screen_name = $screen_name,
            u.sex = $sex, u.home_town = $home_town
        """
        session.run(query, **user.dict())
    return {"message": f"User {user.id} created"}

# Удаление узла (с защитой токена)
@router.delete("/nodes/{node_id}", dependencies=[Depends(verify_token)])
def delete_node(node_id: int):
    with driver.session() as session:
        query = "MATCH (u:User {id: $id}) DETACH DELETE u"
        result = session.run(query, id=node_id)
        if result.consume().counters.nodes_deleted == 0:
            raise HTTPException(status_code=404, detail="Node not found")
    return {"message": f"User {node_id} deleted"}
