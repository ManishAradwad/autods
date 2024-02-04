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
            file_ids=BaseAssistant.file_ids,
        )

    def generate_questions(self, topic, count, multiplier):
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Generate one question based on the topic: {topic}. The output should be just a question and nothing else. For ex. 'What is the capital of Spain?' is an example of the output.",
                }
            ]
        )
        # triggering the first run
        run = self.trigger_run(thread.id, self.questioner_assistant.id)
        # this `messages` will contain only the above prompt
        questions = []
        while len(questions) < count * multiplier:
            # checking if the current run to add a question has completed
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                print("Generating a question...")

            # getting the latest messages from the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # adding the question to the list
            questions.append(messages.data[0].content[0].text.value)

            # logging
            print("New question added! Total questions:", len(questions))
            breakpoint()
            _ = self.client.beta.threads.messages.create(
                thread.id,
                role="user",
                content="Please generate a new question. Make sure new question is not similar to the earlier generated questions.",
            )

            # triggering the next run to add a new question
            run = self.trigger_run(thread.id, self.questioner_assistant.id)

        # this `messages` will contain all the generated questions
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        # this will need some formatting to make it work
        # message = self.client.beta.threads.messages.list(thread_id=thread.id)
        breakpoint()

        return messages
