import pinecone
import requests
import json
import openai


class VectorDBInterface():
    def __init__(self):
        
        pinecone.init(api_key="{API_KEY}", environment="{ENV}")
        self.task_index = pinecone.Index("{INDEX}")

        self.get_info()
        self.get_keys()
        
    def get_keys(self):
        self.turbo_keys = []
        lines = pool.split("\n")
        for line in lines:
            striped = line.strip()
            if striped == "":
                continue
            contents = striped.split("|")
            for cont in contents:
                if cont.startswith("sk-"):
                    self.turbo_keys.append(cont)
    
    def get_info(self):
        
        try:
            info = self.task_index.describe_index_stats()
            self.vector_count = info["total_vector_count"]
            dimension = info['dimension']
            print(info)
            print("Vector Dim", dimension)
            print("Vector Number", self.vector_count)
        except:
            print("Warning: Failed to obtain vector information")


    def generate_embedding(self, text:str):
        url = "https://api.openai.com/v1/embeddings"
        payload = {
            "model": "text-embedding-ada-002",
            "input": text
        }
        for key in self.turbo_keys:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            try:
                res = json.loads(response.text)
                embedding = res['data'][0]['embedding']
                return embedding
            except:
                pass

    def delete_sentence(self, sentence:str):
        
        try:
            self.task_index.delete(sentence)
            print("Success delete sentence:", sentence)
        except:
            print("Warning: Fail to delete sentence", sentence)

    def insert_sentence(self, vec_sentence:str, sentence:str, namespace=""):
        embedding = self.generate_embedding(vec_sentence)
        if embedding:
            try:
                self.task_index.upsert(
                    [(str(self.vector_count),
                    embedding,
                    {"text":sentence, "type":namespace})],
                    # namespace=namespace,
                )
                self.vector_count += 1
            except Exception as e:
                print(e)
                print("Warning: Fail to insert", sentence)
        else:
            print("Warning: Failed to generate embedding for ", sentence)

    def search_similar_sentences(self, query_sentence:str, namespace="", top_k=1):
        
        embedding = self.generate_embedding(query_sentence)
        if embedding:
            try:
                res = self.task_index.query(
                    embedding,
                    top_k=top_k,
                    include_metadata=True,
                    include_values=False,
                    filter={
                        "type": {"$eq": namespace},
                    },)
                print(res)
                return res
            except Exception as e:
                print(e)
                print("Warning: Fail to search similar sentences")
        else:
            print("Warning: Fail to generate embedding")


if __name__ == "__main__":
    VDB = VectorDBInterface()
    VDB.insert_sentence("I plan to go to cinema", "test2")
    VDB.search_similar_sentences("hi, today is good", "test2")
