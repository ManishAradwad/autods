import os
import openai
import jsonlines


class BaseAssistant:
    file_ids = None

    def __init__(self, resources_path, model):
        self.resources_path = resources_path
        self.client = openai.Client()
        self.model = model
        if BaseAssistant.file_ids is None:
            BaseAssistant.file_ids = self.get_file_ids(self.resources_path)

    def get_file_ids(self, resources_path):
        file_ids = []
        for filename in os.listdir(resources_path):
            # Upload a file with an "assistants" purpose
            file = self.client.files.create(  # not sure if this'll work. maybe overwriting the file is fine but idk yet.
                file=open(os.path.join(resources_path, filename), "rb"),
                purpose="assistants",
            )
            file_ids.append(file.id)

        if not file_ids:
            raise ValueError(f"No file found in `{resources_path}`")

        print("Files uploaded successfully")
        return file_ids

    def trigger_run(self, thread_id, assistant_id):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        return run


def save_dataset(dataset, output_file):
    with jsonlines.open(output_file, mode="w") as writer:
        writer.write_all(dataset)
