from bson import ObjectId

def to_object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)

def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    return doc

def serialize_list(docs):
    return [serialize_doc(d) for d in docs]
