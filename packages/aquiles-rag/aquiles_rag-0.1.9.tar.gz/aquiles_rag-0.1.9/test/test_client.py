from aquiles.client import AquilesRAG

client = AquilesRAG(host="https://aquiles-deploy.onrender.com", api_key="dummy-api-key")

print(client.create_index("docs", embeddings_dim=1536, dtype="FLOAT32"))