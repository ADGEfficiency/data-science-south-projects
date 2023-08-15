"""Evaluate the quality of text using OpenAI API function calling.

Example code for the blog post https://www.datasciencesouth.com/blog/openai-functions
"""
import json

import openai
import pydantic


class Evaluation(pydantic.BaseModel):
    """Assessment of a piece of natural language."""
    grammar_errors: list[str] = pydantic.Field(
        default_factory=list, description="grammatical mistakes"
    )
    spelling_errors: list[str] = pydantic.Field(
        default_factory=list, description="spelling mistakes"
    )
    corrected_text: str = pydantic.Field(
        description="the correct text",
        default="a sentence to evaluate"
    )
    is_hard_to_read: bool = pydantic.Field(
        description="if the sentence is diffcult to read",
        default=False
    )



if __name__ == "__main__":
    #  instance of our `pydantic` model
    evaluation = Evaluation()

    #  get a json schema
    schema = evaluation.model_json_schema()

    #  create a function using our schema
    functions = [
        {
            "name": "evaluate_text",
            "description": "Evaluate text for errors.",
            "parameters": {
                "type": schema["type"],
                "properties": schema["properties"],
            },
        }
    ]

    #  text to evaluate
    prompt = "Text to evaulate `The cad jumped over mat.`"

    #  call the openAI api using the `openai` Python package
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {
                "role": "system",
                "content": "You are proof reading text.",
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        functions=functions,
        temperature=0,
    )

    #  extract out the first choice from the response
    choice = response["choices"][0]

    #  make a dictionary from the function call response
    evaluation = json.loads(
        choice["message"]["function_call"]["arguments"]
    )
    print(evaluation)

    #  validate the response
    validated = Evaluation(**evaluation)

    #  check that we have no message from the chat API
    #  not 100% needed
    content = choice["message"]["content"]
    assert content is None
