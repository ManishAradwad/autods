from utils import BaseAssistant, save_dataset
import os
from tqdm import tqdm


class Questioner(BaseAssistant):
    def __init__(self, resources_path, output_path, local_url, model):
        super().__init__(resources_path, output_path, local_url, model)
        if self.local_url:
            self.questioner_assistant = None
        else:
            self.questioner_assistant = self.client.beta.assistants.create(
                name="Questioner",
                instructions="You are a Questioner. Your job is to refer to the resources provided and create questions to be added in the dataset. You can use the retrieval to help you with this task. The response provided should be a question and nothing else.",
                tools=[{"type": "retrieval"}],
                model=self.model,
                file_ids=BaseAssistant.file_ids,
            )

    def generate_questions(self, topic, count, multiplier):
        questions = []
        if self.questioner_assistant is None:
            for _ in range(count * multiplier):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Questioner. Your job is to refer to the resources provided and create questions to be added in the dataset. You can use the retrieval to help you with this task. The response provided should be a question and nothing else.",
                        },
                        {
                            "role": "user",
                            "content": f"Generate one question based on the topic: {topic}. The output should be just a question and nothing else. For ex. 'What is the capital of Spain?' is an example of the output.",
                        },
                    ],
                )
                questions.append(response.choices[0].message.content)
        else:
            thread = None
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
            )  # to update the last question after the loop ends

        # deleting the questioner assistant
        deletion_status = (
            self.client.beta.assistants.delete(
                assistant_id=self.questioner_assistant.id
            )
            if self.questioner_assistant
            else "No assistant used"
        )

        save_dataset(questions, os.path.join(self.output_path, "questions.jsonl"))
        print("Questions generated and saved to questions.jsonl\n")

        return questions, deletion_status
