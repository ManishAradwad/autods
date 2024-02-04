from utils import BaseAssistant
import openai
import os
import time


class Questioner(BaseAssistant):
    def __init__(self, resources_path):
        super().__init__(resources_path)
        self.questioner_assistant = self.client.beta.assistants.create(
            name="Questioner",
            instructions="You are a Questioner. Your job is to refer to the resources provided and create questions to be added in the dataset. You can use the retrieval to help you with this task. The response provided should be a list of questions.",
            tools=[{"type": "retrieval"}],
            model="gpt-3.5-turbo-1106",
            file_ids=self.file_ids,
        )

    def trigger_assistant(self, thread_id):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.questioner_assistant.id,
        )

    def generate_questions(self, topic):
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Generate questions based on the topic: {topic}.",  # the prompt might need some work
            file_ids=self.file_ids,
        )
        self.trigger_assistant(thread.id)

        # Poll the thread until the assistant's response is available
        while True:
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            print("Generating questions...")
            if len(messages.data) > 1:  # The assistant's response is available
                break
            time.sleep(1)  # Wait for a short period before polling again
        # this will need some formatting to make it work
        # message = self.client.beta.threads.messages.list(thread_id=thread.id)
        breakpoint()

        return messages
