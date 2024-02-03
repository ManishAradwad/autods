import os
import openai
import jsonlines


class BaseAssistant:
    def __init__(self, resources_path):
        self.resources_path = resources_path
        self.client = openai.Client()
        self.file_ids = self.get_file_ids(self.resources_path)

    def get_file_ids(self, resources_path):
        file_ids = []
        for filename in os.listdir(resources_path):
            # currently only pdfs are supported
            if filename.endswith(".pdf"):
                # Upload a file with an "assistants" purpose
                file = self.client.files.create(  # not sure if this'll work. maybe overwriting the file is fine but idk yet.
                    file=open(filename, "rb"), purpose="assistants"
                )
                file_ids.append(file.id)
        return file_ids


def save_dataset(dataset, output_file):
    with jsonlines.open(output_file, mode="w") as writer:
        writer.write_all(dataset)
