import pinecone
import requests
import json
import openai


class VectorDBInterface():
    """
    A class for managing vector databases using the Pinecone API.

    Attributes:
    task_index : object
        A Pinecone index object that represents the vector database.
    turbo_keys : list
        A list of secret keys used to validate the connection with the database.
    vector_count : int
        The number of vectors present in the database.

    """

    def __init__(self):
        """
        The constructor for VectorDBInterface class.

        """

        pinecone.init(api_key="{API_KEY}", environment="{ENV}")
        self.task_index = pinecone.Index("{INDEX}")

        self.get_info()
        self.get_keys()
        
    def get_keys(self):
        """
        The function to get the secret keys.

        Retrieves the secret keys from the pool and store them in the list turbo_keys.

        """

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
        """
        The function to get the information about the database.

        Retrieves the statistics of the database such as total vector count and dimension, 
        and store the total vector count in the vector_count attribute.

        Raises:
        Exception: An error occured accessing the database.

        """
        
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
        """
        The function to generate an embedding for the input text.

        Args:
        text (str): The input text.

        Returns:
        list: The embedding of the input text.

        """
        
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
        """
        The function to delete a sentence from the database.

        Args:
        sentence (str): The sentence to be deleted.

        Raises:
        Exception: An error occured deleting the sentence.

        """
        
        try:
            self.task_index.delete(sentence)
            print("Success delete sentence:", sentence)
        except:
            print("Warning: Fail to delete sentence", sentence)

    def insert_sentence(self, vec_sentence:str, sentence:str, namespace=""):
        """
        The function to insert a sentence with its embedding into the database.

        Args:
        vec_sentence (str): The sentence to generate the embedding.
        sentence (str): The sentence to be inserted.
        namespace (str, optional): The namespace of the vector. Defaults to "".

        Raises:
        Exception: An error occured inserting the sentence.

        """
        
        embedding = self.generate_embedding(vec_sentence)
        if embedding:
            try:
                self.task_index.upsert(
                    [(str(self.vector_count),
                    embedding,
                    {"text":sentence, "type":namespace})],
                )
                self.vector_count += 1
            except Exception as e:
                print(e)
                print("Warning: Fail to insert", sentence)
        else:
            print("Warning: Failed to generate embedding for ", sentence)

    def search_similar_sentences(self, query_sentence:str, namespace="", top_k=1):
        """
        The function to search the database for sentences similar to the query sentence.

        Args:
        query_sentence (str): The query sentence.
        namespace (str, optional): The namespace of the vectors. Defaults to "".
        top_k (int, optional): The number of most similar sentences to return. 
            Defaults to 1.

        Returns:
        object: The most similar sentences.

        Raises:
        Exception: An error occured searching the database.

        """
        
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
