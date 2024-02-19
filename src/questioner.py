from utils import BaseAssistant, save_dataset
import os
import time
from tqdm import tqdm


class Questioner(BaseAssistant):
    def __init__(self, resources_path, output_path, local_url, model):
        super().__init__(resources_path, output_path, local_url, model)
        self.questioner_assistant = self.client.beta.assistants.create(
            name="Questioner",
            instructions="You are a Questioner. Your job is to refer to the resources provided and create questions to be added in the dataset. You can use the retrieval to help you with this task. The response provided should be a list of questions.",
            tools=[{"type": "retrieval"}],
            model=self.model,
            file_ids=BaseAssistant.file_ids,
        )

    def generate_questions(self, topic, count, multiplier):
        thread = None
        # this `messages` will contain only the above prompt
        questions = []

        print("Generating questions...")
        for _ in tqdm(range(count * multiplier)):
            if not thread:
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
            else:
                questions = self.update_list(run, self.client, thread.id, questions)

                # logging
                # print("New answer added! Total questions:", len(questions))
                _ = self.client.beta.threads.messages.create(
                    thread.id,
                    role="user",
                    content="Please generate a new question. Make sure new question is not similar to the earlier generated questions.",
                )
                # triggering the next run to add a new answer
                run = self.trigger_run(thread.id, self.questioner_assistant.id)

        questions = self.update_list(
            run, self.client, thread.id, questions
        )  # to update the last answer after the loop ends

        # deleting the questioner assistant
        deletion_status = self.client.beta.assistants.delete(
            assistant_id=self.questioner_assistant.id
        )

        save_dataset(questions, os.path.join(self.output_path, "questions.jsonl"))
        print("Questions generated and saved to questions.jsonl\n")

        return questions, deletion_status
