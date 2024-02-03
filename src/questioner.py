from utils import BaseAssistant
import openai
import os


class Questioner(BaseAssistant):
    def __init__(self, resources_path):
        super().__init__(resources_path)
        self.questioner_assistant = self.client.beta.assistant.create(
            name="Questioner",
            instructions="You are a Questioner. Your job is to refer to the input resources and create questions to be added in the dataset. You can use the retrieval to help you with this task. The response provided should be a list of questions with each line given as 'question'.",
            tools=[{"type": "retrieval"}],
            model="gpt-3.5-turbo-1106",
            file_ids=self.file_ids,
        )

    def generate_questions(self, topic):
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"I want to generate questions based on the topic: {topic}. Refer to the resources provided using Retrieval to generate the questions.",  # the prompt might need some work
        )
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.questioner_assistant.id,
        )
        # this will need some formatting to make it work
        questions = self.client.beta.threads.messages.list(thread_id=thread.id)

        return questions, self.file_ids
