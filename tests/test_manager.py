import unittest
from src.manager import Manager


class TestManager(unittest.TestCase):

    def setUp(self):
        self.resources = "resources"
        self.manager = Manager(
            self.resources, "Generate a dataset for QnA based on football."
        )

    def test_generate_dataset(self):
        result = self.manager.generate_dataset()
        print("check this file: ", result)

    def test_validate_answers(self):
        questions = ["What is football?", "Who invented football?"]
        answers = ["Football is a sport.", "Football was invented by ..."]
        validated_questions, validated_answers = self.manager.validate_answers(
            questions, answers
        )
        self.assertEqual(questions, validated_questions)
        self.assertEqual(answers, validated_answers)


if __name__ == "__main__":
    unittest.main()
