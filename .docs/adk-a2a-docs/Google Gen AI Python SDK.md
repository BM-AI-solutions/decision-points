TITLE: Streaming Text Content with Python Genai
DESCRIPTION: This snippet shows how to use the generate_content_stream method to stream a text response from the Gemini model. It prints each chunk of the response as it arrives, providing real-time feedback.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_37

LANGUAGE: python
CODE:
```
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Generating Content with Text Input
DESCRIPTION: Example of using the generate_content method to get a text response from a Gemini model for a simple query.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_9

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents='Why is the sky blue?'
)
print(response.text)
```

----------------------------------------

TITLE: Creating Client for Gemini Developer API
DESCRIPTION: Code to initialize a client for the Gemini Developer API using an API key.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_2

LANGUAGE: python
CODE:
```
# Only run this block for Gemini Developer API
client = genai.Client(api_key='GEMINI_API_KEY')
```

----------------------------------------

TITLE: Handling API Errors in Python GenAI Client
DESCRIPTION: Demonstrates how to handle errors raised by the model using the APIError class. The code shows error handling for an invalid model name request, accessing the error code and message.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_76

LANGUAGE: python
CODE:
```
try:
    client.models.generate_content(
        model="invalid-model-name",
        contents="What is your name?",
    )
except errors.APIError as e:
    print(e.code) # 404
    print(e.message)
```

----------------------------------------

TITLE: Creating a Client for Gemini Developer API
DESCRIPTION: Code to initialize a client for the Gemini Developer API using an API key.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_2

LANGUAGE: python
CODE:
```
# Only run this block for Gemini Developer API
client = genai.Client(api_key='GEMINI_API_KEY')
```

----------------------------------------

TITLE: Importing Google Gen AI Python Modules
DESCRIPTION: Basic imports required to use the Google Gen AI Python SDK, including the main genai module and types for parameter specification.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_1

LANGUAGE: python
CODE:
```
from google import genai
from google.genai import types
```

----------------------------------------

TITLE: Installing Google Gen AI Python SDK
DESCRIPTION: Command to install the Google Gen AI Python SDK via pip.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_0

LANGUAGE: sh
CODE:
```
pip install google-genai
```

----------------------------------------

TITLE: Generating Content with Text Input
DESCRIPTION: Code to generate content from a text prompt using the Gemini model.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_9

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents='Why is the sky blue?'
)
print(response.text)
```

----------------------------------------

TITLE: Using Pydantic Model for Response Schema in Gemini API
DESCRIPTION: Shows how to use a Pydantic model to define the schema for structured JSON responses from Gemini. This provides type validation and structured data handling.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_31

LANGUAGE: python
CODE:
```
from pydantic import BaseModel


class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=CountryInfo,
    ),
)
print(response.text)
```

----------------------------------------

TITLE: Configuring System Instructions and Generation Parameters
DESCRIPTION: Example of using system instructions and other configuration parameters to control the model's output.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_17

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        max_output_tokens=3,
        temperature=0.3,
    ),
)
print(response.text)
```

----------------------------------------

TITLE: Creating Client Using Environment Variables
DESCRIPTION: Code to initialize a client using the previously set environment variables without explicitly passing parameters.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_6

LANGUAGE: python
CODE:
```
client = genai.Client()
```

----------------------------------------

TITLE: Creating a Client with Environment Variables
DESCRIPTION: Code to initialize a client using environment variables that were previously set.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_6

LANGUAGE: python
CODE:
```
client = genai.Client()
```

----------------------------------------

TITLE: JSON Schema Response with Dictionary Schema in Google Generative AI Python Client
DESCRIPTION: Shows how to define a JSON schema using a dictionary structure rather than a Pydantic model when requesting structured responses from the Google Generative AI model.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_34

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema={
            'required': [
                'name',
                'population',
                'capital',
                'continent',
                'gdp',
                'official_language',
                'total_area_sq_mi',
            ],
            'properties': {
                'name': {'type': 'STRING'},
                'population': {'type': 'INTEGER'},
                'capital': {'type': 'STRING'},
                'continent': {'type': 'STRING'},
                'gdp': {'type': 'INTEGER'},
                'official_language': {'type': 'STRING'},
                'total_area_sq_mi': {'type': 'INTEGER'},
            },
            'type': 'OBJECT',
        },
    ),
)
print(response.text)
```

----------------------------------------

TITLE: Using Typed Configuration for Advanced Parameters
DESCRIPTION: Example of using the Pydantic types for detailed configuration of generation parameters including temperature, top_p, top_k, and more.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_18

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=types.Part.from_text(text='Why is the sky blue?'),
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        seed=5,
        max_output_tokens=100,
        stop_sequences=['STOP!'],
        presence_penalty=0.0,
        frequency_penalty=0.0,
    ),
)

print(response.text)
```

----------------------------------------

TITLE: Using Typed Config with Pydantic
DESCRIPTION: Example of using Pydantic types for configuration parameters in the generate_content method.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_20

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=types.Part.from_text(text='Why is the sky blue?'),
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,

```

----------------------------------------

TITLE: Generating Images with Imagen in Python Genai
DESCRIPTION: This snippet demonstrates how to generate images using the Imagen model. It specifies the prompt, number of images, and configuration options including RAI (Responsible AI) information.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_47

LANGUAGE: python
CODE:
```
# Generate Image
response1 = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt='An umbrella in the foreground, and a rainy night sky in the background',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response1.generated_images[0].image.show()
```

----------------------------------------

TITLE: Streaming Text Content from Gemini Model
DESCRIPTION: Shows how to stream text content from Gemini model, allowing for real-time display of responses as they are generated.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_35

LANGUAGE: python
CODE:
```
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Async Content Generation with Gemini Model in Python
DESCRIPTION: Demonstrates how to use the asynchronous version of generate_content method to request text generation from the Gemini model. This example uses the async/await pattern to generate a 300-word story.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_38

LANGUAGE: python
CODE:
```
response = await client.aio.models.generate_content(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
)

print(response.text)
```

----------------------------------------

TITLE: Creating a Batch Prediction Job in Python
DESCRIPTION: Demonstrates how to create a batch prediction job in Vertex AI. The code specifies the model and source file, with the destination and job display name being automatically populated.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_71

LANGUAGE: python
CODE:
```
# Specify model and source file only, destination and job display name will be auto-populated
job = client.batches.create(
    model='gemini-1.5-flash-002',
    src='bq://my-project.my-dataset.my-table',
)

job
```

----------------------------------------

TITLE: Creating Multimodal Content with Text and Image
DESCRIPTION: Example of combining text and image inputs in a list of parts for multimodal content generation.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_16

LANGUAGE: python
CODE:
```
contents = [
  types.Part.from_text('What is this image about?'),
  types.Part.from_uri(
    file_uri: 'gs://generativeai-downloads/images/scones.jpg',
    mime_type: 'image/jpeg',
  )
]
```

----------------------------------------

TITLE: Creating Mixed Content with Text and Image
DESCRIPTION: Example of creating content with both text and image parts for multimodal generation.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_18

LANGUAGE: python
CODE:
```
contents = [
types.Part.from_text('What is this image about?'),
types.Part.from_uri(
    file_uri: 'gs://generativeai-downloads/images/scones.jpg',
    mime_type: 'image/jpeg',
)
]
```

----------------------------------------

TITLE: Asynchronous Streaming with Python Genai
DESCRIPTION: This snippet shows how to stream content asynchronously from the Gemini model. It uses async for to iterate through the streamed chunks without blocking the main thread.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_41

LANGUAGE: python
CODE:
```
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Creating a URI Part for Image Input
DESCRIPTION: Example of creating a part from a URI that references an image for multimodal input.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_15

LANGUAGE: python
CODE:
```
contents = types.Part.from_uri(
  file_uri: 'gs://generativeai-downloads/images/scones.jpg',
  mime_type: 'image/jpeg',
)
```

----------------------------------------

TITLE: Creating a URI Part for Images
DESCRIPTION: Example of creating a part from a URI for image content.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_17

LANGUAGE: python
CODE:
```
contents = types.Part.from_uri(
file_uri: 'gs://generativeai-downloads/images/scones.jpg',
mime_type: 'image/jpeg',
)
```

----------------------------------------

TITLE: Streaming Chat Responses with Gemini Model in Python
DESCRIPTION: Shows how to create a chat session that streams responses from the Gemini model. This allows for displaying model responses incrementally as they are generated.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_50

LANGUAGE: python
CODE:
```
chat = client.chats.create(model='gemini-2.0-flash-001')
for chunk in chat.send_message_stream('tell me a story'):
    print(chunk.text)
```

----------------------------------------

TITLE: Streaming Image Analysis from Cloud Storage in Gemini
DESCRIPTION: Demonstrates how to stream Gemini responses for image content stored in Google Cloud Storage, using the from_uri method to reference the image.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_36

LANGUAGE: python
CODE:
```
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=[
        'What is this image about?',
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        ),
    ],
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Streaming Image Analysis from Local Files in Gemini
DESCRIPTION: Shows how to stream Gemini responses for image content stored in the local file system, using the from_bytes method to load the image data.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_37

LANGUAGE: python
CODE:
```
YOUR_IMAGE_PATH = 'your_image_path'
YOUR_IMAGE_MIME_TYPE = 'your_image_mime_type'
with open(YOUR_IMAGE_PATH, 'rb') as f:
    image_bytes = f.read()

for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=[
        'What is this image about?',
        types.Part.from_bytes(data=image_bytes, mime_type=YOUR_IMAGE_MIME_TYPE),
    ],
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Using a Fine-tuned Gemini Model in Python
DESCRIPTION: Demonstrates how to use a fine-tuned model for content generation after the tuning job completes. This example accesses the model through its endpoint and generates a response to a prompt.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_64

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents='why is the sky blue?',
)

print(response.text)
```

----------------------------------------

TITLE: Streaming Image-based Content from Local Files
DESCRIPTION: This snippet shows how to process local image files with the Gemini model in streaming mode. It reads the image as bytes and creates a Part object using the from_bytes method.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_39

LANGUAGE: python
CODE:
```
YOUR_IMAGE_PATH = 'your_image_path'
YOUR_IMAGE_MIME_TYPE = 'your_image_mime_type'
with open(YOUR_IMAGE_PATH, 'rb') as f:
    image_bytes = f.read()

for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=[
        'What is this image about?',
        types.Part.from_bytes(data=image_bytes, mime_type=YOUR_IMAGE_MIME_TYPE),
    ],
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Generating Content with Uploaded File
DESCRIPTION: Code to upload a file and generate content based on it using the Gemini Developer API.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_11

LANGUAGE: python
CODE:
```
file = client.files.upload(file='a11.txt')
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=['Could you summarize this file?', file]
)
print(response.text)
```

----------------------------------------

TITLE: Streaming Image-based Content from Google Cloud Storage
DESCRIPTION: This snippet demonstrates how to create a streaming response from the Gemini model when providing an image from Google Cloud Storage. It uses the from_uri method to reference the image.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_38

LANGUAGE: python
CODE:
```
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=[
        'What is this image about?',
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        ),
    ],
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Generating Content with an Uploaded File
DESCRIPTION: Code to upload a file and generate content based on it, demonstrating file handling with Gemini API.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_11

LANGUAGE: python
CODE:
```
file = client.files.upload(file='a11.txt')
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=['Could you summarize this file?', file]
)
print(response.text)
```

----------------------------------------

TITLE: Creating a Content Object with Role and Text Part
DESCRIPTION: Example of creating a structured Content object with a user role and text part for use with generate_content.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_12

LANGUAGE: python
CODE:
```
contents = types.Content(
  role='user',
  parts=[types.Part.from_text(text='Why is the sky blue?')]
)
```

----------------------------------------

TITLE: Async Listing of Tuned Models in Python
DESCRIPTION: Demonstrates how to list tuned models asynchronously. This approach is useful in async environments where non-blocking operations are preferred.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_68

LANGUAGE: python
CODE:
```
async for job in await client.aio.models.list(config={'page_size': 10, 'query_base': False}):
    print(job)
```

----------------------------------------

TITLE: Implementing Automatic Function Calling with Gemini Model in Python
DESCRIPTION: Demonstrates how to define a Python function that can be automatically called by the Gemini model. The model detects when to call the function based on the user's prompt.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_24

LANGUAGE: python
CODE:
```
def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)

print(response.text)
```

----------------------------------------

TITLE: Automatic Python Function Calling in Google Generative AI Python Client
DESCRIPTION: Demonstrates how to use automatic function calling with the Google Generative AI Python client, where a Python function is directly passed to the model and automatically called when the model decides to use it.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_26

LANGUAGE: python
CODE:
```
def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
    ),
)

print(response.text)
```

----------------------------------------

TITLE: Setting API Version for Vertex AI
DESCRIPTION: Code to initialize a Vertex AI client with a specific API version (v1) using http_options.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_7

LANGUAGE: python
CODE:
```
client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1',
    http_options=types.HttpOptions(api_version='v1')
)
```

----------------------------------------

TITLE: Processing Function Call Results with Gemini Model
DESCRIPTION: Shows how to handle function calls received from Gemini, invoke the function, and then pass the function results back to the model for further processing.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_28

LANGUAGE: python
CODE:
```
user_prompt_content = types.Content(
    role='user',
    parts=[types.Part.from_text(text='What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content


try:
    function_result = get_current_weather(
        **function_call_part.function_call.args
    )
    function_response = {'result': function_result}
except (
    Exception
) as e:  # instead of raising the exception, you can let the model handle it
    function_response = {'error': str(e)}


function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(
    role='tool', parts=[function_response_part]
)

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=[
        user_prompt_content,
        function_call_content,
        function_response_content,
    ],
    config=types.GenerateContentConfig(
        tools=[tool],
    ),
)

print(response.text)
```

----------------------------------------

TITLE: Manual Function Invocation and Response Processing in Google Generative AI Python Client
DESCRIPTION: Shows the complete process of manually handling function calls: receiving the function call from the model, invoking the function with the provided arguments, and passing the function response back to the model.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_30

LANGUAGE: python
CODE:
```
user_prompt_content = types.Content(
    role='user',
    parts=[types.Part.from_text(text='What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content


try:
    function_result = get_current_weather(
        **function_call_part.function_call.args
    )
    function_response = {'result': function_result}
except (
    Exception
) as e:  # instead of raising the exception, you can let the model handle it
    function_response = {'error': str(e)}


function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(
    role='tool', parts=[function_response_part]
)

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=[
        user_prompt_content,
        function_call_content,
        function_response_content,
    ],
    config=types.GenerateContentConfig(
        tools=[tool],
    ),
)

print(response.text)
```

----------------------------------------

TITLE: Importing Google Gen AI SDK Modules
DESCRIPTION: Basic import statements for the Google Gen AI SDK, including the main module and types.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_1

LANGUAGE: python
CODE:
```
from google import genai
from google.genai import types
```

----------------------------------------

TITLE: Creating Client for Vertex AI API
DESCRIPTION: Code to initialize a client for the Vertex AI API, requiring project ID and location.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_3

LANGUAGE: python
CODE:
```
# Only run this block for Vertex AI API
client = genai.Client(
    vertexai=True, project='your-project-id', location='us-central1'
)
```

----------------------------------------

TITLE: Creating a Client for Vertex AI API
DESCRIPTION: Code to initialize a client for the Vertex AI API, requiring project ID and location.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_3

LANGUAGE: python
CODE:
```
# Only run this block for Vertex AI API
client = genai.Client(
    vertexai=True, project='your-project-id', location='us-central1'
)
```

----------------------------------------

TITLE: Providing a List of Strings as Content
DESCRIPTION: Example showing how a list of strings is converted to a Content object with multiple parts.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_14

LANGUAGE: python
CODE:
```
contents=['Why is the sky blue?', 'Why is the cloud white?']
```

----------------------------------------

TITLE: Setting Environment Variables for Gemini Developer API
DESCRIPTION: Bash command to set up the necessary environment variable (GOOGLE_API_KEY) for the Gemini Developer API.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_4

LANGUAGE: bash
CODE:
```
export GOOGLE_API_KEY='your-api-key'
```

----------------------------------------

TITLE: Setting Environment Variables for Gemini Developer API
DESCRIPTION: Bash commands to set the GOOGLE_API_KEY environment variable for Gemini Developer API authentication.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_4

LANGUAGE: bash
CODE:
```
export GOOGLE_API_KEY='your-api-key'
```

----------------------------------------

TITLE: Creating Multiple Function Call Parts
DESCRIPTION: Example of creating a list of function call parts for batch processing.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_14

LANGUAGE: python
CODE:
```
contents = [
  types.Part.from_function_call(
    name='get_weather_by_location',
    args={'location': 'Boston'}
  ),
  types.Part.from_function_call(
    name='get_weather_by_location',
    args={'location': 'New York'}
  ),
]
```

----------------------------------------

TITLE: Setting Environment Variables for Vertex AI
DESCRIPTION: Bash commands to set up the necessary environment variables for using Gemini API on Vertex AI.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_5

LANGUAGE: bash
CODE:
```
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

----------------------------------------

TITLE: Setting Environment Variables for Vertex AI
DESCRIPTION: Bash commands to set environment variables for Vertex AI configuration, including project ID and location.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_5

LANGUAGE: bash
CODE:
```
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

----------------------------------------

TITLE: Retrieving File Information in Python Genai
DESCRIPTION: This snippet demonstrates how to retrieve information about a previously uploaded file. It uses the get method with the file name to fetch the file metadata.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_56

LANGUAGE: python
CODE:
```
file1 = client.files.upload(file='2312.11805v3.pdf')
file_info = client.files.get(name=file1.name)
```

----------------------------------------

TITLE: Configuring Safety Settings for Content Generation
DESCRIPTION: Example of setting safety thresholds to control what content the model will generate, blocking potentially harmful content.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_23

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Say something bad.',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_ONLY_HIGH',
            )
        ]
    ),
)
print(response.text)
```

----------------------------------------

TITLE: Configuring Safety Settings in Google Generative AI Python Client
DESCRIPTION: Shows how to configure safety settings when generating content with the Google Generative AI Python client. This example sets a threshold for blocking high-risk hate speech content.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_25

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Say something bad.',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_ONLY_HIGH',
            )
        ]
    ),
)
print(response.text)
```

----------------------------------------

TITLE: Creating a Function Call Part
DESCRIPTION: Example of creating a function call part that specifies a function name and arguments.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_13

LANGUAGE: python
CODE:
```
contents = types.Part.from_function_call(
  name='get_weather_by_location',
  args={'location': 'Boston'}
)
```

----------------------------------------

TITLE: Defining JSON Schema for Gemini Response
DESCRIPTION: Demonstrates how to define a schema directly as a dictionary for structuring JSON responses from Gemini models, providing an alternative to using Pydantic.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_32

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema={
            'required': [
                'name',
                'population',
                'capital',
                'continent',
                'gdp',
                'official_language',
                'total_area_sq_mi',
            ],
            'properties': {
                'name': {'type': 'STRING'},
                'population': {'type': 'INTEGER'},
                'capital': {'type': 'STRING'},
                'continent': {'type': 'STRING'},
                'gdp': {'type': 'INTEGER'},
                'official_language': {'type': 'STRING'},
                'total_area_sq_mi': {'type': 'INTEGER'},
            },
            'type': 'OBJECT',
        },
    ),
)
print(response.text)
```

----------------------------------------

TITLE: JSON Schema Response with Pydantic Model in Google Generative AI Python Client
DESCRIPTION: Demonstrates how to use a Pydantic model to define the schema for structured JSON responses from the Google Generative AI model, ensuring the model returns data in a specific format.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_33

LANGUAGE: python
CODE:
```
from pydantic import BaseModel


class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int


response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=CountryInfo,
    ),
)
print(response.text)
```

----------------------------------------

TITLE: Accessing Function Calls from Response in Google Generative AI Python Client
DESCRIPTION: Shows how to access the function calls returned by the model when automatic function calling is disabled in the Google Generative AI Python client.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_28

LANGUAGE: python
CODE:
```
function_calls: Optional[List[types.FunctionCall]] = response.function_calls
```

----------------------------------------

TITLE: Implementing Enum Response Schema with Text Format in Gemini
DESCRIPTION: Shows how to restrict Gemini responses to predefined enum values with text/x.enum format, ensuring the model returns only valid categorical values.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_33

LANGUAGE: python
CODE:
```
class InstrumentEnum(Enum):
  PERCUSSION = 'Percussion'
  STRING = 'String'
  WOODWIND = 'Woodwind'
  BRASS = 'Brass'
  KEYBOARD = 'Keyboard'

response = client.models.generate_content(
      model='gemini-2.0-flash-001',
      contents='What instrument plays multiple notes at once?',
      config={
          'response_mime_type': 'text/x.enum',
          'response_schema': InstrumentEnum,
      },
  )
print(response.text)
```

----------------------------------------

TITLE: Configuring Custom Response Schema with Enum in Python Genai
DESCRIPTION: This snippet demonstrates how to use a custom Enum schema to get structured responses from the Gemini model using 'text/x.enum' response type. It sets up an enum of instrument types and gets a categorized response.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_36

LANGUAGE: python
CODE:
```
class InstrumentEnum(Enum):
    PERCUSSION = 'Percussion'
    STRING = 'String'
    WOODWIND = 'Woodwind'
    BRASS = 'Brass'
    KEYBOARD = 'Keyboard'

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What instrument plays multiple notes at once?',
    config={
        'response_mime_type': 'application/json',
        'response_schema': InstrumentEnum,
    },
)
print(response.text)
```

----------------------------------------

TITLE: Generating Videos with Veo Model in Python
DESCRIPTION: Shows how to generate videos using the Veo model and handle long-running operations. This example generates a 5-second video at 24 fps and includes prompt enhancement. This feature requires allowlist access.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_48

LANGUAGE: python
CODE:
```
# Create operation
operation = client.models.generate_videos(
    model='veo-2.0-generate-001',
    prompt='A neon hologram of a cat driving at top speed',
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        fps=24,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

# Poll operation
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.result.generated_videos[0].video
video.show()
```

----------------------------------------

TITLE: Setting API Version for Gemini Developer API
DESCRIPTION: Code to initialize a Gemini Developer API client with a specific API version (v1alpha) using http_options.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_8

LANGUAGE: python
CODE:
```
client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(api_version='v1alpha')
)
```

----------------------------------------

TITLE: Setting API Version for Gemini Developer API
DESCRIPTION: Code to initialize a Gemini Developer API client with a specific API version (v1alpha) using http_options.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_8

LANGUAGE: python
CODE:
```
# Only run this block for Gemini Developer API
client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(api_version='v1alpha')
)
```

----------------------------------------

TITLE: Paginating Through Tuning Jobs in Python
DESCRIPTION: Demonstrates how to use pagination when listing tuning jobs. This approach allows for retrieving and processing large numbers of jobs in manageable chunks.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_72

LANGUAGE: python
CODE:
```
pager = client.tunings.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

----------------------------------------

TITLE: Listing Available Base Models
DESCRIPTION: Example of listing all available base models with a simple iteration approach.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_19

LANGUAGE: python
CODE:
```
for model in client.models.list():
    print(model)
```

----------------------------------------

TITLE: Listing Base Models in Google Generative AI Python Client
DESCRIPTION: Shows how to retrieve a list of available models using the Google Generative AI Python client. The code demonstrates both simple listing and paginated results.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_21

LANGUAGE: python
CODE:
```
for model in client.models.list():
    print(model)
```

----------------------------------------

TITLE: Paginated Model Listing in Google Generative AI Python Client
DESCRIPTION: Demonstrates how to use pagination when listing models with the Google Generative AI Python client, including setting page size and navigating through pages of results.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_22

LANGUAGE: python
CODE:
```
pager = client.models.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

----------------------------------------

TITLE: Listing Models with Paging
DESCRIPTION: Example of using paging to list models with a specified page size and navigation between pages.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_20

LANGUAGE: python
CODE:
```
pager = client.models.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

----------------------------------------

TITLE: Listing Models Asynchronously
DESCRIPTION: Example of listing models using asynchronous iteration for more efficient processing.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_21

LANGUAGE: python
CODE:
```
async for job in await client.aio.models.list():
    print(job)
```

----------------------------------------

TITLE: Listing Tuned Models Asynchronously in Python
DESCRIPTION: Demonstrates asynchronous listing of tuned models with pagination. The code shows both async iteration through all models and accessing specific pages of results asynchronously.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_67

LANGUAGE: python
CODE:
```
async for job in await client.aio.models.list(config={'page_size': 10, 'query_base': False}}):
    print(job)
```

LANGUAGE: python
CODE:
```
async_pager = await client.aio.models.list(config={'page_size': 10, 'query_base': False}})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

----------------------------------------

TITLE: Asynchronous Model Listing in Google Generative AI Python Client
DESCRIPTION: Shows how to asynchronously list models using the Google Generative AI Python client's async interface. This is useful for non-blocking operations in async applications.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_23

LANGUAGE: python
CODE:
```
async for job in await client.aio.models.list():
    print(job)
```

----------------------------------------

TITLE: Asynchronous Paginated Model Listing in Google Generative AI Python Client
DESCRIPTION: Demonstrates asynchronous pagination when listing models with the Google Generative AI Python client, allowing for efficient processing of large result sets in async contexts.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_24

LANGUAGE: python
CODE:
```
async_pager = await client.aio.models.list(config={'page_size': 10})
print(async_pager.page_size)
print(async_pager[0])
await async_pager.next_page()
print(async_pager[0])
```

----------------------------------------

TITLE: Embedding Text Content with Python Genai
DESCRIPTION: This snippet shows how to generate text embeddings using the text-embedding model. Embeddings convert text into numerical vectors that capture semantic meaning.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_45

LANGUAGE: python
CODE:
```
response = client.models.embed_content(
    model='text-embedding-004',
    contents='why is the sky blue?',
)
print(response)
```

----------------------------------------

TITLE: Manually Declaring a Function for Gemini Function Calling
DESCRIPTION: Demonstrates how to manually declare a function and its schema for Gemini function calling. This approach provides explicit control over function definitions and parameters.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_27

LANGUAGE: python
CODE:
```
function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'location': types.Schema(
                type='STRING',
                description='The city and state, e.g. San Francisco, CA',
            ),
        },
        required=['location'],
    ),
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.function_calls[0])
```

----------------------------------------

TITLE: Manual Function Declaration for Function Calling in Google Generative AI Python Client
DESCRIPTION: Demonstrates how to manually declare a function schema and pass it as a tool to the model in the Google Generative AI Python client, instead of using automatic function support.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_29

LANGUAGE: python
CODE:
```
function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'location': types.Schema(
                type='STRING',
                description='The city and state, e.g. San Francisco, CA',
            ),
        },
        required=['location'],
    ),
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[tool],
    ),
)
print(response.function_calls[0])
```

----------------------------------------

TITLE: Uploading Files in Python Genai
DESCRIPTION: This snippet shows how to upload PDF files to the Gemini Developer API. It uploads multiple files and prints information about the uploaded files.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_55

LANGUAGE: python
CODE:
```
file1 = client.files.upload(file='2312.11805v3.pdf')
file2 = client.files.upload(file='2403.05530.pdf')

print(file1)
print(file2)
```

----------------------------------------

TITLE: Disabling Automatic Function Calling in Gemini API
DESCRIPTION: Shows how to disable automatic function calling when passing a Python function as a tool to the Gemini model. This gives more control over when functions are executed.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_25

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
  model='gemini-2.0-flash-001',
  contents='What is the weather like in Boston?',
  config=types.GenerateContentConfig(
    tools=[get_current_weather],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
      disable=True
    ),
  ),
)
```

----------------------------------------

TITLE: Disabling Automatic Function Calling in Google Generative AI Python Client
DESCRIPTION: Shows how to disable automatic function calling when using the Google Generative AI Python client, allowing for manual handling of function calls returned by the model.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_27

LANGUAGE: python
CODE:
```
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    ),
)
```

----------------------------------------

TITLE: Counting Tokens in Text with Gemini Model in Python
DESCRIPTION: Demonstrates how to use the count_tokens method to determine how many tokens are in a given piece of text. This is useful for managing token limits in API requests.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_40

LANGUAGE: python
CODE:
```
response = client.models.count_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

----------------------------------------

TITLE: Accessing Function Calls from Gemini Response
DESCRIPTION: Shows how to retrieve the function calls returned by the model when automatic function calling is disabled. This allows manual handling of function execution.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_26

LANGUAGE: python
CODE:
```
function_calls: Optional[List[types.FunctionCall]] = response.function_calls
```

----------------------------------------

TITLE: Disabling Automatic Function Calling in 'ANY' Mode with Gemini
DESCRIPTION: Shows how to configure function calling mode to 'ANY' while disabling automatic function calling, giving more explicit control over when functions are executed.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_29

LANGUAGE: python
CODE:
```
def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

----------------------------------------

TITLE: Creating and Monitoring Batch Prediction Jobs in Python with Google GenAI Client
DESCRIPTION: Shows how to create a batch prediction job, retrieve its status, and wait for completion using the Google GenAI client. It includes specifying the model and source file, and monitoring the job state.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_74

LANGUAGE: python
CODE:
```
job = client.batches.create(
    model='gemini-1.5-flash-002',
    src='bq://my-project.my-dataset.my-table',
)

job
```

LANGUAGE: python
CODE:
```
job = client.batches.get(name=job.name)

job.state
```

LANGUAGE: python
CODE:
```
completed_states = set(
    [
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
        'JOB_STATE_PAUSED',
    ]
)

while job.state not in completed_states:
    print(job.state)
    job = client.batches.get(name=job.name)
    time.sleep(30)

job
```

----------------------------------------

TITLE: Limiting Automatic Function Call Turns in Gemini AI
DESCRIPTION: Demonstrates how to set a limit on the number of automatic function call turns by configuring maximum remote calls. This helps control the depth of function calling.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_30

LANGUAGE: python
CODE:
```
def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=2
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

----------------------------------------

TITLE: Limiting Automatic Function Call Turns in Google Generative AI Python Client
DESCRIPTION: Shows how to limit the number of automatic function call turns by setting a maximum remote calls limit when using the Google Generative AI Python client with ANY mode in function calling.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_32

LANGUAGE: python
CODE:
```
def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=2
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

----------------------------------------

TITLE: Polling Tuning Job Status Until Completion in Python
DESCRIPTION: Shows how to poll the status of a tuning job until it completes. This approach checks the job status periodically to determine when the tuning process has finished.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_63

LANGUAGE: python
CODE:
```
import time

running_states = set(
    [
        'JOB_STATE_PENDING',
        'JOB_STATE_RUNNING',
    ]
)

while tuning_job.state in running_states:
    print(tuning_job.state)
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(10)
```

----------------------------------------

TITLE: Async Token Counting with Gemini Model in Python
DESCRIPTION: Demonstrates the asynchronous version of the count_tokens method. This allows for token counting operations to be performed without blocking the main thread.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_42

LANGUAGE: python
CODE:
```
response = await client.aio.models.count_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

----------------------------------------

TITLE: Batch Text Embedding with Dimension Configuration in Python
DESCRIPTION: Demonstrates how to generate embeddings for multiple text inputs simultaneously with a custom output dimensionality. This approach is more efficient than making separate API calls for each text.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_44

LANGUAGE: python
CODE:
```
# multiple contents with config
response = client.models.embed_content(
    model='text-embedding-004',
    contents=['why is the sky blue?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality=10),
)

print(response)
```

----------------------------------------

TITLE: Asynchronous Token Counting with Python Genai
DESCRIPTION: This snippet demonstrates how to count tokens asynchronously using the aio client. It performs the same function as count_tokens but in a non-blocking manner.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_44

LANGUAGE: python
CODE:
```
response = await client.aio.models.count_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

----------------------------------------

TITLE: Computing Tokens with Gemini Model in Vertex AI
DESCRIPTION: Shows how to use the compute_tokens method which is specifically available in Vertex AI. This functionality provides more detailed token information than the standard count_tokens method.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_41

LANGUAGE: python
CODE:
```
response = client.models.compute_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

----------------------------------------

TITLE: Creating Content with a Content Instance
DESCRIPTION: Example of creating a Content object with a user role and text part for generating content.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_12

LANGUAGE: python
CODE:
```
contents = types.Content(
role='user',
parts=[types.Part.from_text(text='Why is the sky blue?')]
)
```

----------------------------------------

TITLE: Computing Tokens with Vertex AI
DESCRIPTION: This snippet shows how to compute tokens using the Vertex AI platform. The compute_tokens method is only available when using Vertex AI as the backend.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_43

LANGUAGE: python
CODE:
```
response = client.models.compute_tokens(
    model='gemini-2.0-flash-001',
    contents='why is the sky blue?',
)
print(response)
```

----------------------------------------

TITLE: Generating Images with Imagen Model in Python
DESCRIPTION: Demonstrates how to generate images using the Imagen model. This functionality includes options to specify the number of images, include responsible AI reasons, and define the output format.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_45

LANGUAGE: python
CODE:
```
# Generate Image
response1 = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt='An umbrella in the foreground, and a rainy night sky in the background',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response1.generated_images[0].image.show()
```

----------------------------------------

TITLE: Editing Images with Imagen in Vertex AI
DESCRIPTION: This snippet demonstrates how to edit images using the Imagen model. It uses reference images and masks to specify which parts of the image to modify, allowing for targeted edits like background replacement.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_49

LANGUAGE: python
CODE:
```
# Edit the generated image from above
from google.genai.types import RawReferenceImage, MaskReferenceImage

raw_ref_image = RawReferenceImage(
    reference_id=1,
    reference_image=response1.generated_images[0].image,
)

# Model computes a mask of the background
mask_ref_image = MaskReferenceImage(
    reference_id=2,
    config=types.MaskReferenceConfig(
        mask_mode='MASK_MODE_BACKGROUND',
        mask_dilation=0,
    ),
)

response3 = client.models.edit_image(
    model='imagen-3.0-capability-001',
    prompt='Sunlight and clear sky',
    reference_images=[raw_ref_image, mask_ref_image],
    config=types.EditImageConfig(
        edit_mode='EDIT_MODE_INPAINT_INSERTION',
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response3.generated_images[0].image.show()
```

----------------------------------------

TITLE: Upscaling Generated Images with Imagen Model in Vertex AI
DESCRIPTION: Shows how to upscale a previously generated image using the Imagen model's upscale_image functionality. This is only available in Vertex AI and allows for higher resolution outputs.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_46

LANGUAGE: python
CODE:
```
# Upscale the generated image from above
response2 = client.models.upscale_image(
    model='imagen-3.0-generate-001',
    image=response1.generated_images[0].image,
    upscale_factor='x2',
    config=types.UpscaleImageConfig(
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response2.generated_images[0].image.show()
```

----------------------------------------

TITLE: Configuring Custom Embeddings with Python Genai
DESCRIPTION: This snippet demonstrates how to generate embeddings for multiple content items with custom configuration. It sets the output dimensionality to control the size of the embedding vectors.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_46

LANGUAGE: python
CODE:
```
# multiple contents with config
response = client.models.embed_content(
    model='text-embedding-004',
    contents=['why is the sky blue?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality=10),
)

print(response)
```

----------------------------------------

TITLE: Listing Tuning Jobs in Python
DESCRIPTION: Demonstrates how to list tuning jobs with pagination. The code shows both iterating through all jobs and accessing specific pages of results.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_69

LANGUAGE: python
CODE:
```
for job in client.tunings.list(config={'page_size': 10}):
    print(job)
```

LANGUAGE: python
CODE:
```
pager = client.tunings.list(config={'page_size': 10})
print(pager.page_size)
print(pager[0])
pager.next_page()
print(pager[0])
```

----------------------------------------

TITLE: Generating Videos with Veo in Python Genai
DESCRIPTION: This snippet demonstrates how to generate videos using the Veo model. It creates an asynchronous operation to generate a video with specified parameters and then polls until completion.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_50

LANGUAGE: python
CODE:
```
# Create operation
operation = client.models.generate_videos(
    model='veo-2.0-generate-001',
    prompt='A neon hologram of a cat driving at top speed',
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        fps=24,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

# Poll operation
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.result.generated_videos[0].video
video.show()
```

----------------------------------------

TITLE: Async Chat Sessions with Gemini Model in Python
DESCRIPTION: Demonstrates how to create an asynchronous chat session with the Gemini model. This allows for non-blocking message sending and response handling in async environments.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_51

LANGUAGE: python
CODE:
```
chat = client.aio.chats.create(model='gemini-2.0-flash-001')
response = await chat.send_message('tell me a story')
print(response.text)
```

----------------------------------------

TITLE: Creating and Using Chat Sessions with Gemini Model in Python
DESCRIPTION: Demonstrates how to create a chat session for multi-turn conversations with the Gemini model. This example shows how to send a message and retrieve the response.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_49

LANGUAGE: python
CODE:
```
chat = client.chats.create(model='gemini-2.0-flash-001')
response = chat.send_message('tell me a story')
print(response.text)
```

----------------------------------------

TITLE: Asynchronous Streaming Chat with Python Genai
DESCRIPTION: This snippet demonstrates how to stream chat responses asynchronously. It combines the benefits of streaming with non-blocking async execution for optimal performance.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_54

LANGUAGE: python
CODE:
```
chat = client.aio.chats.create(model='gemini-2.0-flash-001')
async for chunk in await chat.send_message_stream('tell me a story'):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Downloading Sample PDF Files using gsutil in Command Line
DESCRIPTION: Shows how to download sample PDF files from Google Cloud Storage using the gsutil command-line tool. These files are used for demonstrating file operations with the GenAI client.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_53

LANGUAGE: cmd
CODE:
```
!gsutil cp gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf .
!gsutil cp gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf .
```

----------------------------------------

TITLE: Asynchronous Chat Sessions with Python Genai
DESCRIPTION: This snippet shows how to create asynchronous chat sessions for non-blocking conversations. It uses the aio client to avoid blocking the main thread during model processing.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_53

LANGUAGE: python
CODE:
```
chat = client.aio.chats.create(model='gemini-2.0-flash-001')
response = await chat.send_message('tell me a story')
print(response.text)
```

----------------------------------------

TITLE: Uploading Files to Gemini API in Python
DESCRIPTION: Demonstrates how to upload PDF files to the Gemini Developer API. This functionality is only available in the Gemini Developer API and not in Vertex AI.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_54

LANGUAGE: python
CODE:
```
file1 = client.files.upload(file='2312.11805v3.pdf')
file2 = client.files.upload(file='2403.05530.pdf')

print(file1)
print(file2)
```

----------------------------------------

TITLE: Deleting Files from Gemini API in Python
DESCRIPTION: Demonstrates how to delete a previously uploaded file from the Gemini Developer API. This allows for managing storage and removing files that are no longer needed.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_56

LANGUAGE: python
CODE:
```
file3 = client.files.upload(file='2312.11805v3.pdf')

client.files.delete(name=file3.name)
```

----------------------------------------

TITLE: Streaming Content Generation with Gemini Model in Python
DESCRIPTION: Shows how to stream generated content from the Gemini model using asynchronous iteration. This approach receives and processes content chunks as they become available rather than waiting for the complete response.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_39

LANGUAGE: python
CODE:
```
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

----------------------------------------

TITLE: Deleting Files in Python Genai
DESCRIPTION: This snippet shows how to delete files that were previously uploaded to the Gemini Developer API. It uploads a file and then immediately deletes it using the file name.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_57

LANGUAGE: python
CODE:
```
file3 = client.files.upload(file='2312.11805v3.pdf')

client.files.delete(name=file3.name)
```

----------------------------------------

TITLE: Creating Cached Content for PDFs with Gemini Model in Python
DESCRIPTION: Shows how to create cached content from PDF files for more efficient processing with the Gemini model. This example handles both Vertex AI and Gemini Developer API approaches with different file URI formats.
SOURCE: https://github.com/googleapis/python-genai/blob/main/README.md#2025-04-11_snippet_57

LANGUAGE: python
CODE:
```
if client.vertexai:
    file_uris = [
        'gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
        'gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
    ]
else:
    file_uris = [file1.uri, file2.uri]

cached_content = client.caches.create(
    model='gemini-1.5-pro-002',
    config=types.CreateCachedContentConfig(
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_uri(
                        file_uri=file_uris[0], mime_type='application/pdf'
                    ),
                    types.Part.from_uri(
                        file_uri=file_uris[1],
                        mime_type='application/pdf',
                    ),
                ],
            )
        ],
        system_instruction='What is the sum of the two pdfs?',
        display_name='test cache',
        ttl='3600s',
    ),
)
```

----------------------------------------

TITLE: Deleting a Batch Prediction Job in Python
DESCRIPTION: Shows how to delete a batch prediction job using its name. This code removes the job resource from the system.
SOURCE: https://github.com/googleapis/python-genai/blob/main/docs/_sources/index.rst.txt#2025-04-11_snippet_75

LANGUAGE: python
CODE:
```
# Delete the job resource
delete_job = client.batches.delete(name=job.name)

delete_job
```