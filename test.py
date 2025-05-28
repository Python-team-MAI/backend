from app.api_v1.assistant.service import yandex_service


index_id = yandex_service.create_new_index(["test_knowledge_base/celevoe.md"])

print(index_id)