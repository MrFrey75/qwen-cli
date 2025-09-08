# Qwen-CLI: Configuration Options and Defaults

## Purpose:

This document describes the configuration options available in the config/config.json file. This file controls the behavior and settings for the conversational language model interface.
Example config.json

``` json
{
    "assistant-name" : "Gwen",
    "user-name":"Arthur",
    "model": "qwen:latest",
    "host": "http://localhost:11434",
    "history_dir": "logs",
    "max_messages": 20,
    "system_prompt": "You are <assitant-name>, a helpful assistant. Always use the conversation history to answer. If the user has provided personal details (like name) earlier in this session, use them when helpful. Keep answers concise.",
    "title": "session",
    "logging_level": "info",
    "response_format": "markdown",
    "session_timeout_minutes": 30,
    "temperature": 0.7,
    "persona": {
        "role": "helpful assistant",
        "tone": "friendly",
        "style": "conversational",
        "verbosity": "concise"
    }
}
```

## Configuration Field Details

### assistant-name

    Type: string

    Default: "Gwen"

    Description: This sets the name of the AI assistant. This name is inserted into the system_prompt and can influence how the model refers to itself. Changing this allows you to give the AI a different persona or identity.

### user-name

    Type: string

    Default: "Arthur"

    Description: The name used to identify the user. This is primarily for the AI's internal context to better personalize responses, as it will be able to remember and reference the user by name if the system_prompt allows it.

### model

    Type: string

    Default: "qwen:latest"

    Description: Specifies which language model to use. This string must match the name of a model available on the specified host. For example, you might change this to "llama2:7b" or "mistral:latest" if those models are available on your server.

### host

    Type: string

    Default: "http://localhost:11434"

    Description: The address of the server hosting the language model. The default is the standard local host and port for many popular LLM platforms like Ollama. If you are running the server on a different machine or port, or a cloud service, you must update this URL.

### history_dir

    Type: string

    Default: "logs"

    Description: The file system path where conversation history logs will be saved. This is a path relative to the project's root directory. The path must be valid and writable by the application.

### max_messages

    Type: number

    Default: 20

    Description: The maximum number of messages (pairs of user and assistant responses) from the conversation history to be included in the context of each new request sent to the model. A larger number provides more context, but can increase processing time and resource usage.

### system_prompt

    Type: string

    Default: "You are <assitant-name>, a helpful assistant. Always use the conversation history to answer. If the user has provided personal details (like name) earlier in this session, use them when helpful. Keep answers concise."

    Description: This is a powerful instruction that defines the AI's core behavior. It works in conjunction with the persona settings to form the final set of instructions sent to the model. You can use this to set global rules for the AI, while the persona object provides a more granular way to fine-tune its traits.

### title

    Type: string

    Default: "session"

    Description: A descriptive title for the current conversation session. This is often used to name the output log file, making it easier to organize and find specific conversation histories later.

### logging_level

    Type: string

    Default: "info"

    Description: Controls the verbosity of the application's output. Possible values include "debug", "info", "warn", and "error". This is useful for troubleshooting and monitoring the application's behavior.

### response_format

    Type: string

    Default: "markdown"

    Description: Specifies the format of the AI's response. This can be used to generate structured output for different use cases. Possible values include "markdown" for rich text formatting and "plain_text" for simple, unformatted output.

### session_timeout_minutes

    Type: number

    Default: 30

    Description: The number of minutes of inactivity before the current session is automatically ended. A value of 0 means the session will never time out. This is helpful for managing resources and ensuring context is refreshed for new conversations.

### temperature

    Type: number

    Default: 0.7

    Description: A value that controls the randomness of the language model's output. Values closer to 0 will result in more predictable and factual responses, while values closer to 1 will produce more creative and varied results.

### persona

    Type: object

    Default:

    {
        "role": "helpful assistant",
        "tone": "friendly",
        "style": "conversational",
        "verbosity": "concise"
    }

    Description: This object contains granular settings to define the AI's personality traits.

### persona.role

    Type: string

    Default: "helpful assistant"

    Description: Defines the role or expertise of the AI. For example, you could set this to "creative writer", "technical expert", or "humorous travel guide".

### persona.tone

    Type: string

    Default: "friendly"

    Description: Describes the emotional tone of the responses. Possible values include "friendly", "formal", "humorous", or "sarcastic".

### persona.style

    Type: string

    Default: "conversational"

    Description: Controls the overall writing style of the responses. This could be "conversational", "technical", or "journalistic".

### persona.verbosity

    Type: string

    Default: "concise"

    Description: Specifies the preferred length of responses. Possible values include "concise", "standard", or "detailed".