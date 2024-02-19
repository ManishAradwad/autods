from questioner import Questioner
from answerer import Answerer
from utils import BaseAssistant, save_dataset
import time
import random
from tqdm import tqdm
import os


class Manager(BaseAssistant):
    def __init__(
        self,
        resources_path,
        output_path,
        prompt,
        local_url=None,
        model="gpt-3.5-turbo-1106",
    ):
        super().__init__(resources_path, output_path, local_url, model)
        # in future can provide functionaluty to let user decide the model specific to both q and a
        self.questioner = Questioner(
            self.resources_path, self.output_path, local_url, self.model
        )
        self.answerer = Answerer(
            self.resources_path, self.output_path, local_url, self.model
        )
        self.topic = self.extract_topic(prompt)
        self.validator_assistant = self.client.beta.assistants.create(
            name="Manager",
            instructions=f'You are a Manager who oversees the creation of a dataset based on the {self.topic}. You are given a question-answer pair. Your job is to refer to the input resources and verify whether the answer is correct for the correspoding question. You can use the retrieval to help you with this task. The response provided should be either "Valid" or "Invalid". The value should be "Valid" if the provided `answer` answers the given `question` and "Invalid" if it does not. For instance, if the input question is \'What is the capital of France?\' and the answer is \'Paris\', the response should be "Valid". If the input question is \'What is the capital of France?\' and the answer is \'Spain\', the response should be "Invalid". ADD "VALID" OR "INVALID" WORD IN THE RESPONSE. IF THE ANSWER MENTIONS SOMETHING LIKE `I could not find answer specific to the question in the provided documents`, THEN THE RESPONSE SHOULD BE "INVALID".',
            tools=[{"type": "retrieval"}],
            model=self.model,
            file_ids=BaseAssistant.file_ids,
        )

    def extract_topic(self, prompt):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that helps people extract the main topic from a given prompt. In the response, please provide only the name of the topic and nothing else. For instance if the prompt is: 'Generate a dataset for QnA based on football', The main topic is: Football.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        topic = completion.choices[0].message
        return topic.content

    def generate_dataset(self, type_ds="train.jsonl", count=1, multiplier=5):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)
        print("The topic extracted from the given prompt is:", self.topic)
        questions, _ = self.questioner.generate_questions(self.topic, count, multiplier)
        answers, _ = self.answerer.generate_answers(questions)
        validated_questions, validated_answers = self.validate_answers(
            questions, answers
        )
        dataset = [
            {"text": f"\\nQ:{q}\\nA:{a}"}
            for q, a in zip(validated_questions, validated_answers)
        ]
        save_dataset(dataset, os.path.join(self.output_path, type_ds))

        return type_ds

    def validate(self, run, thread_id, lst):
        # checking if the current run to add a question has completed
        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )
            time.sleep(1)
            # print("Validating a QnA pair...")

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value

        if "invalid" in response.lower():
            lst.append(0)
        else:
            lst.append(1)
        return lst

    def validate_answers(self, questions, answers):
        # randomise the order of questions and answers list but the order should be same for both
        paired = list(zip(questions, answers))
        random.shuffle(paired)
        questions, answers = zip(*paired)
        thread = None

        result = []

        print("Validating questions...")
        for question, answer in tqdm(zip(questions, answers), total=len(questions)):
            if not thread:
                thread = self.client.beta.threads.create(
                    messages=[
                        {
                            "role": "user",
                            "content": f"I want to validate this question-answer pair: Question-{question}\nAnswer-{answer}.",
                        }
                    ]
                )
                # triggering the first run
                run = self.trigger_run(thread.id, self.validator_assistant.id)
            else:
                result = self.validate(run, thread.id, result)
                # logging
                # print("New question verified! Total verified:", len(questions))
                _ = self.client.beta.threads.messages.create(
                    thread.id,
                    role="user",
                    content=f"Please verify this next question-answer pair:\nQuestion-{question}\nAnswer-{answer}",
                )
                # triggering the next run to add a new question
                run = self.trigger_run(thread.id, self.validator_assistant.id)

        result = self.validate(
            run, thread.id, result
        )  # to update the last answer after the loop ends

        # deleting the questioner assistant
        _ = self.client.beta.assistants.delete(assistant_id=self.validator_assistant.id)

        validated_questions = [q for q, r in zip(questions, result) if r == 1]
        validated_answers = [a for a, r in zip(answers, result) if r == 1]

        save_dataset(result, os.path.join(self.output_path, "validation_result.jsonl"))
        print("Answers validated and the results saved to validation_result.jsonl\n")

        # deleting the files
        for file_id in BaseAssistant.file_ids:
            self.client.files.delete(file_id)
        print("Files deleted successfully")

        return validated_questions, validated_answers
