# Automated Tool for Creating Datasets

This project contains an automated tool for creating datasets for fine-tuning Language Learning Models (LLMs). The tool is inspired by AutoGPT and uses the OpenAI API to generate a Question-Answer dataset on a specific topic provided by the user. You can add files (pdf only for now) in the `resources` folder. These files will be used for dataset creation using Retrieval Augmented Generation.

NOTE: [According to OpenAI](https://platform.openai.com/docs/assistants/how-it-works/creating-assistants])

> You can attach a maximum of 20 files per Assistant, and they can be at most 512 MB each. The size of all the files uploaded by your organization should not exceed 100 GB. You can request an increase in this storage limit using our help center. In addition to the 512 MB file size limit, each file can only contain 2,000,000 tokens. Assistant or Message creation will fail if any attached files exceed the token limit.

Please keep this in mind while adding the files

## Project Structure

The project is structured as follows:

- `src/questioner.py`: Contains the `Questioner` class for generating questions related to a given topic.
- `src/answerer.py`: Contains the `Answerer` class for generating answers to the provided questions.
- `src/manager.py`: Contains the `Manager` class for coordinating the `Questioner` and `Answerer` classes and validating the generated answers.
- `src/utils.py`: Contains utility functions used by the `Questioner`, `Answerer`, and `Manager` classes.
- `tests`: Contains unit tests.
- `resources`: Directory for storing the text resources provided by the user.

## Setup

1. Clone the repository.
2. Install the required Python dependencies listed in `requirements.txt`.
3. Place your text resources in the `resources` directory.

## Usage

1. Check the parameter values in `src/run.py`
```bash
python3 src/run.py
```

## Testing

To run the unit tests, navigate to the `tests` directory and run the following command:

```bash
python3 -m unittest
```

## Contributing

Contributions are welcome. Please submit a pull request with your changes.

## License

This project is licensed under the MIT License.

## TODO:

high priority:

- [ ] Improve the validator reply prompt. Validator responses are based on a very loose rule of “if ‘valid’ in response then append 1 else 0”. Try fixing that(not sure how to do this.) 
- [ ] Add the open source model support along with GPT
    - [ ] May need llama-index since it seems its mainly for RAG. llamaindex seems like an OSS alternative to how openai uses RAG in their api. So LocalAI may need llama-index
    - [ ] Makes sense to use a vector db since files will be referred again and again
low priority:

- [ ] Use function calling for formatting the model responses
- [ ] Add an example for dataset format
- [ ] Add the ability to generate QnA based on images as well by adding vision tool
- [ ] Sometimes answers contain the prompt used for getting the response. Maybe related to the model. 