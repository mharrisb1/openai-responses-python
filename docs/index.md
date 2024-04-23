# Introduction

Pytest plugin for automatically mocking OpenAI requests.

## Installation

Available on [PyPi](https://pypi.org/project/openai-responses/)

=== "pip"

    ```shell
    pip install openai-responses
    ```

=== "poetry"

    ```shell
    poetry add --group dev openai-responses
    ```

## Why use this?

For building production-ready AI features, you need to add tests to your code. A lot of work and attention is going into evals but the performance of the AI model is only part of the testing story.
Your AI features live with all of the other code in your app and you need to be able to test those interations.

To avoid actually using the OpenAI endpoints in your tests - which cost money and are probabilistic - you can mock those calls so that everything works the way it will in production but with
but with predetermined responses.
