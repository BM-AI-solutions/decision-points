TITLE: Defining FunctionDeclarationsTool Property Type in TypeScript
DESCRIPTION: Type definition for the functionDeclarations property that accepts an optional array of FunctionDeclaration objects. This property enables passing up to 64 function declarations to the model which can be called during model responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclarationstool.functiondeclarations.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionDeclarations?: FunctionDeclaration[];
```

----------------------------------------

TITLE: Defining FunctionDeclarationsTool Interface in TypeScript
DESCRIPTION: The FunctionDeclarationsTool interface definition enables a system to interact with external systems to perform actions outside the model's knowledge and scope. It contains an optional functionDeclarations property that accepts an array of FunctionDeclaration objects.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclarationstool.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface FunctionDeclarationsTool 
```

----------------------------------------

TITLE: GenerativeModel Class Definition in TypeScript
DESCRIPTION: Base class definition for generative model APIs that provides core functionality for interacting with Google's generative AI models. This class serves as the main entry point for making API calls to generate content, embed content, and manage chat sessions.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GenerativeModel
```

----------------------------------------

TITLE: Defining the ChatSession.sendMessageStream() Method Signature in TypeScript
DESCRIPTION: Method signature for sendMessageStream which sends a chat message and receives the response as a GenerateContentStreamResult. The method accepts a string or array of string/Part objects as the request, and optional SingleRequestOptions that override global RequestOptions.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession.sendmessagestream.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
sendMessageStream(request: string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<GenerateContentStreamResult>;
```

----------------------------------------

TITLE: Defining FunctionDeclaration Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionDeclaration interface, which represents a function that can be used as a Tool by the model and executed by the client. It includes properties for the function name, description, and parameters.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclaration.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface FunctionDeclaration 
```

----------------------------------------

TITLE: Defining GenerateContentStreamResult Interface in TypeScript
DESCRIPTION: This code snippet defines the GenerateContentStreamResult interface, which contains two properties: 'response' for the aggregated response promise, and 'stream' for iterating over content chunks as they arrive.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentstreamresult.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerateContentStreamResult 
{
  response: Promise<EnhancedGenerateContentResponse>;
  stream: AsyncGenerator<EnhancedGenerateContentResponse>;
}
```

----------------------------------------

TITLE: Defining GenerateContentRequest Interface in TypeScript
DESCRIPTION: This code snippet defines the GenerateContentRequest interface, which extends BaseParams and includes properties for content generation requests. It specifies optional properties for cached content, system instructions, tool configurations, and an array of content items.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentrequest.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerateContentRequest extends BaseParams {
  cachedContent?: string;
  contents: Content[];
  systemInstruction?: string | Part | Content;
  toolConfig?: ToolConfig;
  tools?: Tool[];
}
```

----------------------------------------

TITLE: Defining FunctionCallingConfig Interface in TypeScript
DESCRIPTION: This TypeScript interface defines the configuration options for function calling in the Generative AI library. It includes optional properties for specifying allowed function names and the function calling mode.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncallingconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionCallingConfig 
```

----------------------------------------

TITLE: Instantiating a GenerativeModel in TypeScript
DESCRIPTION: Constructor signature for creating a new instance of the GenerativeModel class. It requires an API key, model parameters, and optional request options for configuration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(apiKey: string, modelParams: ModelParams, _requestOptions?: RequestOptions);
```

----------------------------------------

TITLE: Defining systemInstruction Property in TypeScript
DESCRIPTION: This code snippet shows the TypeScript signature for the systemInstruction property of the StartChatParams interface. It is an optional property that can accept a string, Part, or Content type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.startchatparams.systeminstruction.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
systemInstruction?: string | Part | Content;
```

----------------------------------------

TITLE: Defining the GoogleGenerativeAI Class in Typescript
DESCRIPTION: Defines the `GoogleGenerativeAI` class, which serves as the main entry point for the library. It allows users to obtain a `GenerativeModel` instance and to retrieve a generative model instance from cached content.  The constructor accepts an API key.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_4

LANGUAGE: typescript
CODE:
```
//@public
export class GoogleGenerativeAI {
    constructor(apiKey: string);
    // (undocumented)
    apiKey: string;
    getGenerativeModel(modelParams: ModelParams, requestOptions?: RequestOptions): GenerativeModel;
    getGenerativeModelFromCachedContent(cachedContent: CachedContent, modelParams?: Partial<ModelParams>, requestOptions?: RequestOptions): GenerativeModel;
}
```

----------------------------------------

TITLE: Defining Executable Code Language Enum in TypeScript
DESCRIPTION: This snippet exports a TypeScript enum named ExecutableCodeLanguage, which categorizes the languages that can be utilized within the generative AI model. The enum provides a way to refer to the language types in a structured manner, enhancing type safety and readability within the API documentation. The members include 'LANGUAGE_UNSPECIFIED' for unspecified languages and 'PYTHON' for Python language.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.executablecodelanguage.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum ExecutableCodeLanguage 

```

----------------------------------------

TITLE: Initializing Generative Model with TypeScript
DESCRIPTION: Method signature for creating a GenerativeModel instance with optional model parameters and request options. Used to configure and instantiate AI model interactions in the Google Generative AI framework.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeai.getgenerativemodel.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
getGenerativeModel(modelParams: ModelParams, requestOptions?: RequestOptions): GenerativeModel;
```

----------------------------------------

TITLE: Running JavaScript Samples with Node.js
DESCRIPTION: This snippet demonstrates how to run the provided JavaScript sample files using Node.js from the command line. It serves as the basic execution instruction for each sample file.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/samples/README.md#2025-04-21_snippet_0

LANGUAGE: shell
CODE:
```
"node function_calling.js"
```

----------------------------------------

TITLE: ChatSession Class Declaration
DESCRIPTION: This code snippet shows the declaration of the `ChatSession` class in TypeScript. The class is exported, making it available for use in other modules. It serves as a container for managing chat sessions with a generative AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class ChatSession 
```

----------------------------------------

TITLE: Constructing a new ChatSession instance in TypeScript
DESCRIPTION: Creates a new instance of the ChatSession class with required API key and model parameters, plus optional parameters for chat configuration and request options.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(apiKey: string, model: string, params?: StartChatParams, _requestOptions?: RequestOptions);
```

----------------------------------------

TITLE: Defining Function Calling Interfaces for Google Generative AI
DESCRIPTION: TypeScript interfaces for function calling features in the Google Generative AI API. Includes function declarations, calls, responses, and configuration options.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai-server.api.md#2025-04-21_snippet_6

LANGUAGE: typescript
CODE:
```
// @public
export interface FunctionCall {
    // (undocumented)
    args: object;
    // (undocumented)
    name: string;
}

// @public (undocumented)
export interface FunctionCallingConfig {
    // (undocumented)
    allowedFunctionNames?: string[];
    // (undocumented)
    mode?: FunctionCallingMode;
}

// @public (undocumented)
export enum FunctionCallingMode {
    // (undocumented)
    ANY = "ANY",
    // (undocumented)
    AUTO = "AUTO",
    // (undocumented)
    MODE_UNSPECIFIED = "MODE_UNSPECIFIED",
    // (undocumented)
    NONE = "NONE"
}

// @public
export interface FunctionCallPart {
    // (undocumented)
    codeExecutionResult?: never;
    // (undocumented)
    executableCode?: never;
    // (undocumented)
    fileData?: never;
    // (undocumented)
    functionCall: FunctionCall;
    // (undocumented)
    functionResponse?: never;
    // (undocumented)
    inlineData?: never;
    // (undocumented)
    text?: never;
}

// @public
export interface FunctionDeclaration {
    description?: string;
    name: string;
    parameters?: FunctionDeclarationSchema;
}

// @public
export interface FunctionDeclarationSchema {
    description?: string;
    properties: {
        [k: string]: FunctionDeclarationSchemaProperty;
    };
    required?: string[];
    type: SchemaType;
}

// @public
export type FunctionDeclarationSchemaProperty = Schema;

// @public
export interface FunctionDeclarationsTool {
    functionDeclarations?: FunctionDeclaration[];
}

// @public
export interface FunctionResponse {
    // (undocumented)
    name: string;
    // (undocumented)
    response: object;
}

// @public
export interface FunctionResponsePart {
    // (undocumented)
    codeExecutionResult?: never;
    // (undocumented)
    executableCode?: never;
    // (undocumented)
    fileData?: never;
    // (undocumented)
    functionCall?: never;
    // (undocumented)
    functionResponse: FunctionResponse;
    // (undocumented)
    inlineData?: never;
    // (undocumented)
    text?: never;
}
```

----------------------------------------

TITLE: TextPart.text Property Signature
DESCRIPTION: This code snippet shows the TypeScript signature of the `text` property of the `TextPart` class. The property is of type string and represents the text content associated with the TextPart.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.textpart.text.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"text: string;"
```

----------------------------------------

TITLE: Defining ObjectSchema Interface in TypeScript
DESCRIPTION: This code snippet defines the ObjectSchema interface, which extends BaseSchema. It specifies the structure for describing JSON objects with properties, optional required fields, and a fixed type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.objectschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ObjectSchema extends BaseSchema {
  properties: { [k: string]: Schema };
  required?: string[];
  type: typeof SchemaType.OBJECT;
}
```

----------------------------------------

TITLE: Defining generateContent() Method Signature in TypeScript
DESCRIPTION: This code snippet defines the signature of the generateContent() method for the GenerativeModel class. It accepts a request parameter of various types and an optional requestOptions parameter, returning a Promise that resolves to a GenerateContentResult.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.generatecontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
generateContent(request: GenerateContentRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<GenerateContentResult>;
```

----------------------------------------

TITLE: Defining BaseParams Interface in TypeScript
DESCRIPTION: This code snippet defines the BaseParams interface, which includes optional properties for generationConfig and safetySettings. It serves as a base structure for parameters used in various methods of the generative AI package.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.baseparams.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface BaseParams {
  generationConfig?: GenerationConfig;
  safetySettings?: SafetySetting[];
}
```

----------------------------------------

TITLE: Embedding Content Method Signature in TypeScript
DESCRIPTION: Method signature for embedContent that accepts content to be embedded in various formats (EmbedContentRequest, string, or array of strings/Parts) and optional request configuration. Returns a Promise containing the embedding response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.embedcontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
embedContent(request: EmbedContentRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<EmbedContentResponse>;
```

----------------------------------------

TITLE: Defining the GenerateContentResponse Interface in Typescript
DESCRIPTION: Defines the structure of a `GenerateContentResponse`. It includes optional `candidates` (an array of `GenerateContentCandidate` objects), `promptFeedback` (of type `PromptFeedback`), and `usageMetadata` (of type `UsageMetadata`). It represents the standard response format from a generate content request.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_2

LANGUAGE: typescript
CODE:
```
//@public
export interface GenerateContentResponse {
    candidates?: GenerateContentCandidate[];
    promptFeedback?: PromptFeedback;
    usageMetadata?: UsageMetadata;
}
```

----------------------------------------

TITLE: Defining GenerationConfig Interface in TypeScript
DESCRIPTION: This code snippet defines the GenerationConfig interface, which includes various optional properties for configuring content generation requests. The interface provides options for controlling output tokens, penalties, response formats, and other generation parameters.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerationConfig 
```

----------------------------------------

TITLE: Defining ExecutableCodePart TypeScript Interface
DESCRIPTION: Declares an interface for capturing executable code parts with various optional properties for code execution, function calls, and data management
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.executablecodepart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ExecutableCodePart {
  codeExecutionResult?: never;
  executableCode: ExecutableCode;
  fileData?: never;
  functionCall?: never;
  functionResponse?: never;
  inlineData?: never;
  text?: never;
}
```

----------------------------------------

TITLE: Defining GenerateContentResponse Interface in TypeScript
DESCRIPTION: TypeScript interface declaration for GenerateContentResponse that specifies the structure of content generation responses. It includes optional properties for candidates (array of possible responses), promptFeedback (content filter feedback), and usageMetadata (token usage information).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerateContentResponse 
```

----------------------------------------

TITLE: Uploading Files with GoogleAIFileManager in TypeScript
DESCRIPTION: Method signature for uploading a file with the GoogleAIFileManager class. Takes a file path, file metadata, and optional request options. Returns a Promise that resolves to an UploadFileResponse object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager.uploadfile.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
uploadFile(filePath: string, fileMetadata: FileMetadata, requestOptions?: SingleRequestOptions): Promise<UploadFileResponse>;
```

----------------------------------------

TITLE: Defining toolConfig Property in GenerateContentRequest Interface (TypeScript)
DESCRIPTION: This code snippet defines the optional toolConfig property of type ToolConfig in the GenerateContentRequest interface. It is part of the type definition for configuring tool-related options in content generation requests.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentrequest.toolconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
toolConfig?: ToolConfig;
```

----------------------------------------

TITLE: Declaring GoogleGenerativeAI Class in TypeScript
DESCRIPTION: This snippet shows the TypeScript declaration for the GoogleGenerativeAI class, which is the main entry point for the Google Generative AI SDK.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeai.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleGenerativeAI 
```

----------------------------------------

TITLE: Defining FunctionDeclarationSchema Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionDeclarationSchema interface, which includes properties for description, properties, required parameters, and type. It is used to specify the structure of parameters for function declarations in the generative AI context.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclarationschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionDeclarationSchema 
```

----------------------------------------

TITLE: Defining the GenerateContentRequest Interface in Typescript
DESCRIPTION: Defines the structure for a `GenerateContentRequest`, which extends `BaseParams`. It includes properties for cached content, the content itself (`Content[]`), an optional system instruction which could be string, Part or Content, an optional ToolConfig, and an optional array of Tools.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_1

LANGUAGE: typescript
CODE:
```
//@public
export interface GenerateContentRequest extends BaseParams {
    cachedContent?: string;
    // (undocumented)
    contents: Content[];
    // (undocumented)
    systemInstruction?: string | Part | Content;
    // (undocumented)
    toolConfig?: ToolConfig;
    // (undocumented)
    tools?: Tool[];
}
```

----------------------------------------

TITLE: ModelParams Interface Definition
DESCRIPTION: This code snippet defines the `ModelParams` interface in TypeScript. It extends the `BaseParams` interface and includes optional properties for cached content, model name, system instructions, tool configurations, and a list of tools. This interface is used to configure generative models within the Google Generative AI library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.modelparams.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ModelParams extends BaseParams 
```

----------------------------------------

TITLE: Defining StartChatParams Interface in TypeScript
DESCRIPTION: TypeScript interface definition for StartChatParams which extends BaseParams and provides parameters for initializing a chat session with a generative model. This interface includes optional properties for configuring history, system instructions, tool configurations, and cached content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.startchatparams.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface StartChatParams extends BaseParams 
```

----------------------------------------

TITLE: Defining response Property in GenerateContentResult Class (TypeScript)
DESCRIPTION: This code snippet defines the 'response' property for the GenerateContentResult class. The property is of type EnhancedGenerateContentResponse, which likely contains detailed information about the generated content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentresult.response.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
response: EnhancedGenerateContentResponse;
```

----------------------------------------

TITLE: Defining EnhancedGenerateContentResponse Interface in TypeScript
DESCRIPTION: Interface definition that extends GenerateContentResponse and provides helper methods for accessing generated content. Includes methods for retrieving function calls and text content from response candidates.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.enhancedgeneratecontentresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface EnhancedGenerateContentResponse extends GenerateContentResponse 
```

----------------------------------------

TITLE: StartChatParams.tools property in TypeScript
DESCRIPTION: The `tools` property is an optional array of `Tool` objects. It allows you to provide tools that the model can use during the chat session. If no tools are provided, the model will not have access to any external functionalities.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.startchatparams.tools.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"tools?: Tool[];"
```

----------------------------------------

TITLE: Defining Content Interface in TypeScript for @google/generative-ai
DESCRIPTION: This code snippet defines the Content interface used for both prompts and response candidates in the @google/generative-ai package. It includes two properties: parts (an array of Part objects) and role (a string).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.content.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface Content 
{
  parts: Part[];
  role: string;
}
```

----------------------------------------

TITLE: Defining UsageMetadata Interface in Typescript
DESCRIPTION: This TypeScript interface, UsageMetadata, is intended for use in generative AI frameworks. Its purpose is to track and provide metadata on token usage in generation requests. It depends on the TypeScript environment and requires no additional libraries. Key properties include `promptTokenCount`, `cachedContentTokenCount`, `candidatesTokenCount`, and `totalTokenCount`, which represent different token counts associated with a generation request. The interface expects numeric counts as inputs and outputs and has optional and required fields. Token count details may constrain its implementation.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.usagemetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface UsageMetadata 
```

----------------------------------------

TITLE: Defining Content Parts Array in TypeScript
DESCRIPTION: Declares a parts property as an array of Part objects, used for handling different content types in generative AI interactions
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.content.parts.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
parts: Part[];
```

----------------------------------------

TITLE: Defining Generative AI Tool Type (TypeScript)
DESCRIPTION: This code defines the `Tool` type as a union of `FunctionDeclarationsTool`, `CodeExecutionTool`, and `GoogleSearchRetrievalTool`. This allows the model to use functions, execute code, or perform Google searches to access external information.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.tool.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare type Tool = FunctionDeclarationsTool | CodeExecutionTool | GoogleSearchRetrievalTool;
```

----------------------------------------

TITLE: ChatSession.sendMessage() method signature
DESCRIPTION: This code snippet shows the method signature of `sendMessage` in the `ChatSession` class. It takes a request (either a string or an array of strings/Parts) and optional request options, returning a Promise that resolves to a `GenerateContentResult`. The `SingleRequestOptions` allows overriding the global `RequestOptions`.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession.sendmessage.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
sendMessage(request: string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<GenerateContentResult>;
```
```

----------------------------------------

TITLE: Defining contents Property in GenerateContentRequest Interface (TypeScript)
DESCRIPTION: This code snippet defines the contents property for the GenerateContentRequest interface. It specifies that contents is an array of Content objects, which likely represent the input data for content generation.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentrequest.contents.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
contents: Content[];
```

----------------------------------------

TITLE: RequestOptions Interface Definition in TypeScript
DESCRIPTION: Defines the `RequestOptions` interface used for configuring requests to the Generative Language API. It includes optional properties for specifying the API client, API version, base URL, custom headers, and request timeout. This interface is used when calling `getGenerativeModel()` or `GoogleAIFileManager()` to customize the API request.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.requestoptions.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface RequestOptions 
```

----------------------------------------

TITLE: Defining Harm Probability Enum - TypeScript
DESCRIPTION: This TypeScript code defines an enumeration, HarmProbability, which categorizes the probability levels (UNSPECIFIED, HIGH, LOW, MEDIUM, NEGLIGIBLE) of content being unsafe. It is part of the @google/generative-ai module and helps in hazard assessment frameworks within generative AI systems.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.harmprobability.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum HarmProbability
```

LANGUAGE: typescript
CODE:
```
HARM_PROBABILITY_UNSPECIFIED = "HARM_PROBABILITY_UNSPECIFIED"
```

LANGUAGE: typescript
CODE:
```
HIGH = "HIGH"
```

LANGUAGE: typescript
CODE:
```
LOW = "LOW"
```

LANGUAGE: typescript
CODE:
```
MEDIUM = "MEDIUM"
```

LANGUAGE: typescript
CODE:
```
NEGLIGIBLE = "NEGLIGIBLE"
```

----------------------------------------

TITLE: Building and Testing the generative-ai-js Project Locally
DESCRIPTION: A sequence of commands to set up the development environment, build the project, run tests, generate documentation, format code, and create a changeset summary. These steps ensure that contributions meet the project's standards before submission.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/contributing.md#2025-04-21_snippet_0

LANGUAGE: bash
CODE:
```
cd generative-ai-js
npm install
npm run build
npm run test
npm run docs
npm run format
npx @changesets/cli
```

----------------------------------------

TITLE: Defining functionCallingConfig Property in ToolConfig Interface in TypeScript
DESCRIPTION: TypeScript signature for the functionCallingConfig property within the ToolConfig interface. This property is typed as FunctionCallingConfig and is used to configure function calling capabilities.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.toolconfig.functioncallingconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionCallingConfig: FunctionCallingConfig;
```

----------------------------------------

TITLE: Defining BatchEmbedContentsResponse Interface in TypeScript
DESCRIPTION: This code snippet defines the BatchEmbedContentsResponse interface, which is used as the return type for the GenerativeModel.batchEmbedContents() method. It contains a single property 'embeddings' of type ContentEmbedding[].
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.batchembedcontentsresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface BatchEmbedContentsResponse {
    embeddings: ContentEmbedding[];
}
```

----------------------------------------

TITLE: Defining EmbedContentResponse Interface in TypeScript
DESCRIPTION: This code snippet defines the EmbedContentResponse interface, which is the response type for the GenerativeModel.embedContent() method. It contains a single property 'embedding' of type ContentEmbedding.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.embedcontentresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface EmbedContentResponse 
{
  embedding: ContentEmbedding;
}
```

----------------------------------------

TITLE: Content Parts Property Definition in Typescript
DESCRIPTION: Defines the `parts` property as an array of `Part` objects within the `Content` class. This property is essential for representing structured content in generative AI models, allowing for multiple distinct parts within a single content object. Each element in the array should conform to the `Part` interface.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.content.parts.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"parts: Part[];"
```

----------------------------------------

TITLE: Defining EnhancedGenerateContentResponse.text Property in TypeScript
DESCRIPTION: Defines the 'text' property as a method that returns a string. This method assembles text from all Parts of the first candidate in the response. It throws an exception if the prompt or candidate was blocked.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.enhancedgeneratecontentresponse.text.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
text: () => string;
```

----------------------------------------

TITLE: Streaming Content Generation Result in TypeScript
DESCRIPTION: Defines an asynchronous generator interface for streaming content generation responses from the Generative AI library. Allows iterative processing of generated content with enhanced type support.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentstreamresult.stream.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
stream: AsyncGenerator<EnhancedGenerateContentResponse>;
```

----------------------------------------

TITLE: Retrieving Chat History in TypeScript with Google Generative AI SDK
DESCRIPTION: Gets the chat history from a ChatSession. This method returns a Promise that resolves to an array of Content objects. It excludes blocked prompts and candidates, as well as prompts that generated blocked candidates.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession.gethistory.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
getHistory(): Promise<Content[]>;
```

----------------------------------------

TITLE: Defining mode Property in FunctionCallingConfig Interface - TypeScript
DESCRIPTION: Signature definition for the optional mode property in the FunctionCallingConfig interface, which accepts a value of type FunctionCallingMode.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncallingconfig.mode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mode?: FunctionCallingMode;
```

----------------------------------------

TITLE: Defining Possible Roles in TypeScript
DESCRIPTION: This code snippet defines a read-only array named `POSSIBLE_ROLES` containing string literals representing the possible roles: 'user', 'model', 'function', and 'system'. It is a constant declaration which aims to standardize the roles available within the generative AI model. This avoids the use of arbitrary strings, promoting type safety and consistency in role assignments.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.possible_roles.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
POSSIBLE_ROLES: readonly ["user", "model", "function", "system"]
```
```

----------------------------------------

TITLE: Defining Content Part Type in TypeScript
DESCRIPTION: Union type representing multiple part types including text, data, function call/response, file data, and code execution parts
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.part.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type Part = TextPart | InlineDataPart | FunctionCallPart | FunctionResponsePart | FileDataPart | ExecutableCodePart | CodeExecutionResultPart;
```

----------------------------------------

TITLE: Defining FileMetadata Interface in TypeScript
DESCRIPTION: This TypeScript interface defines the structure for metadata that can be provided during a file upload. It includes optional properties for display name and name, along with a required property for MIME type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileMetadata {
}
```

----------------------------------------

TITLE: Defining the SafetySetting Interface in TypeScript
DESCRIPTION: TypeScript interface definition for SafetySetting which can be included in request parameters to control content safety filtering. It contains two properties: category (specifying the type of harm to check for) and threshold (defining the level at which content should be blocked).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.safetysetting.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface SafetySetting 
```

----------------------------------------

TITLE: Defining Schema Type Using TypeScript
DESCRIPTION: This snippet exports a type definition for Schema that can represent multiple types of data structures. It allows for flexibility in defining data according to OpenAPI standards and can handle various data formats such as strings, numbers, booleans, arrays, and objects. This type is foundational for constructing a flexible generative AI API.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.schema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type Schema = StringSchema | NumberSchema | IntegerSchema | BooleanSchema | ArraySchema | ObjectSchema;
```

----------------------------------------

TITLE: Defining HarmCategory Enum - TypeScript
DESCRIPTION: This snippet declares an enumeration named HarmCategory in TypeScript, which categorizes potential harmful content prompts that the application should block. The enum members represent different types of harm categories such as civic integrity, dangerous content, harassment, hate speech, sexually explicit content, and unspecified harm. These values are essential for enforcing content guidelines in generative AI applications.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.harmcategory.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
export declare enum HarmCategory {
    HARM_CATEGORY_CIVIC_INTEGRITY = "HARM_CATEGORY_CIVIC_INTEGRITY",
    HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT",
    HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT",
    HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH",
    HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    HARM_CATEGORY_UNSPECIFIED = "HARM_CATEGORY_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Starting a Chat Session in Generative AI
DESCRIPTION: Initializes a new ChatSession with optional configuration parameters. Enables multi-turn conversational interactions with the generative AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.startchat.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
startChat(startChatParams?: StartChatParams): ChatSession;
```

----------------------------------------

TITLE: Defining FileMetadata Interface in TypeScript for Google Generative AI
DESCRIPTION: This code snippet defines the FileMetadata interface which specifies the metadata structure required when uploading files to the Generative AI API. It includes a required mimeType property and optional displayName and name properties.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileMetadata 

```

----------------------------------------

TITLE: Defining Content Interfaces for Google Generative AI
DESCRIPTION: TypeScript interfaces for content management in the Google Generative AI API. These interfaces define the structure for cached content and related operations.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai-server.api.md#2025-04-21_snippet_1

LANGUAGE: typescript
CODE:
```
// @public
export interface CachedContent extends CachedContentBase {
    createTime?: string;
    // (undocumented)
    name?: string;
    ttl?: string;
    updateTime?: string;
}

// @public (undocumented)
export interface CachedContentBase {
    // (undocumented)
    contents: Content[];
    // (undocumented)
    displayName?: string;
    expireTime?: string;
    // (undocumented)
    model?: string;
    // (undocumented)
    systemInstruction?: string | Part | Content;
    // (undocumented)
    toolConfig?: ToolConfig;
    // (undocumented)
    tools?: Tool[];
}

// @public
export interface CachedContentCreateParams extends CachedContentBase {
    ttlSeconds?: number;
}

// @public
export interface CachedContentUpdateInputFields {
    // (undocumented)
    expireTime?: string;
    // (undocumented)
    ttlSeconds?: number;
}

// @public
export interface CachedContentUpdateParams {
    // (undocumented)
    cachedContent: CachedContentUpdateInputFields;
    updateMask?: string[];
}

// @internal
export interface _CachedContentUpdateRequest {
    // (undocumented)
    cachedContent: _CachedContentUpdateRequestFields;
    updateMask?: string[];
}

// @internal
export interface _CachedContentUpdateRequestFields {
    // (undocumented)
    expireTime?: string;
    // (undocumented)
    ttl?: string;
}
```

----------------------------------------

TITLE: Defining SafetySetting.category Property
DESCRIPTION: This snippet defines the 'category' property of type 'HarmCategory' for the SafetySetting. The property is essential for categorizing harm levels in generative AI's safety settings. This enables developers to specify the category of harm when implementing safety measures in AI models.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.safetysetting.category.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
category: HarmCategory;
```

----------------------------------------

TITLE: Defining SafetyRating Interface in TypeScript
DESCRIPTION: TypeScript interface definition for SafetyRating which represents a safety rating associated with content generated by the Generative AI API. It contains two properties: category of type HarmCategory and probability of type HarmProbability.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.safetyrating.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface SafetyRating 
```

----------------------------------------

TITLE: Example Function Parameters Schema Definition
DESCRIPTION: Example showing how to define required and optional parameters in the schema format. Demonstrates defining a required string parameter 'param1' and an optional integer parameter 'param2'.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclaration.parameters.md#2025-04-21_snippet_1

LANGUAGE: plaintext
CODE:
```
param1:
  type: STRING
param2:
 type: INTEGER
required:
  - param1
```

----------------------------------------

TITLE: Example of FunctionDeclaration Parameters Schema
DESCRIPTION: An example showing how to define function parameters with one required parameter ('param1') and one optional parameter ('param2'). The schema uses the object type with property definitions and a required array.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclaration.parameters.md#2025-04-21_snippet_1

LANGUAGE: plaintext
CODE:
```
param1:

  type: STRING
param2:

 type: INTEGER
required:

  - param1
```

----------------------------------------

TITLE: Constructing GoogleAIFileManager Instance in TypeScript
DESCRIPTION: This code snippet shows the constructor signature for creating a new instance of the GoogleAIFileManager class. It takes an apiKey as a required parameter and an optional _requestOptions parameter.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(apiKey: string, _requestOptions?: RequestOptions);
```

----------------------------------------

TITLE: Defining functionCallingConfig Property in TypeScript
DESCRIPTION: This snippet defines the 'functionCallingConfig' property within the ToolConfig interface, which holds configuration options for function calling in TypeScript. It is a key part of the tool's setup for handling function calls. The main parameter is 'FunctionCallingConfig', which outlines the necessary structure for the configuration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.toolconfig.functioncallingconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionCallingConfig: FunctionCallingConfig;
```

----------------------------------------

TITLE: Defining FinishReason Enum in TypeScript for Google Generative AI
DESCRIPTION: Declaration of the FinishReason enum which provides standardized codes for why a generative model's response terminated. This includes reasons like reaching token limits, safety boundaries, or natural stopping points.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.finishreason.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum FinishReason 
```

----------------------------------------

TITLE: Defining Candidates Property in TypeScript
DESCRIPTION: This snippet declares the candidates property within the GenerateContentResponse interface. It is defined as an optional array of GenerateContentCandidate objects, which represent the various candidate responses generated by the AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentresponse.candidates.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
candidates?: GenerateContentCandidate[];
```

----------------------------------------

TITLE: Defining Properties in FunctionDeclarationSchema in TypeScript
DESCRIPTION: TypeScript signature for the properties field of the FunctionDeclarationSchema interface. This field defines a dictionary of properties where the keys are property names and values are FunctionDeclarationSchemaProperty objects that describe the format and constraints of each parameter.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclarationschema.properties.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
properties: {
        [k: string]: FunctionDeclarationSchemaProperty;
    };
```

----------------------------------------

TITLE: Defining Property in GenerateContentRequest
DESCRIPTION: This TypeScript snippet defines an optional 'tools' property in the GenerateContentRequest type, expecting an array of 'Tool' objects. It allows specifying tools that can be used in a generative AI request. The 'Tool' type must be defined elsewhere in the codebase. This snippet appears in the context of an automatically generated documentation file.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentrequest.tools.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
tools?: Tool[];
```

----------------------------------------

TITLE: Defining TextPart Interface in TypeScript
DESCRIPTION: This code snippet defines the TextPart interface, which represents a content part for a text string. It includes several optional properties and one required 'text' property of type string.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.textpart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface TextPart 
{
  codeExecutionResult?: never;
  executableCode?: never;
  fileData?: never;
  functionCall?: never;
  functionResponse?: never;
  inlineData?: never;
  text: string;
}
```

----------------------------------------

TITLE: Defining functionDeclarations Property in FunctionDeclarationsTool Class in TypeScript
DESCRIPTION: Optional property that accepts an array of FunctionDeclaration objects to be passed to the model with the current user query. The model may call these functions in its response, and the user should provide function responses in the next turn. Limited to a maximum of 64 function declarations.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclarationstool.functiondeclarations.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionDeclarations?: FunctionDeclaration[];
```

----------------------------------------

TITLE: Defining the GenerativeModel Class in Typescript
DESCRIPTION: Defines the `GenerativeModel` class, which is used to interact with generative AI models. It includes methods for generating content, embedding content, counting tokens, and starting a chat session. The constructor takes an API key, model parameters, and optional request options.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_3

LANGUAGE: typescript
CODE:
```
//@public
export class GenerativeModel {
    constructor(apiKey: string, modelParams: ModelParams, _requestOptions?: RequestOptions);
    // (undocumented)
    apiKey: string;
    batchEmbedContents(batchEmbedContentRequest: BatchEmbedContentsRequest, requestOptions?: SingleRequestOptions): Promise<BatchEmbedContentsResponse>;
    // (undocumented)
    cachedContent: CachedContent;
    countTokens(request: CountTokensRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<CountTokensResponse>;
    embedContent(request: EmbedContentRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<EmbedContentResponse>;
    generateContent(request: GenerateContentRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<GenerateContentResult>;
    generateContentStream(request: GenerateContentRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<GenerateContentStreamResult>;
    // (undocumented)
    generationConfig: GenerationConfig;
    // (undocumented)
    model: string;
    // (undocumented)
    safetySettings: SafetySetting[];
    startChat(startChatParams?: StartChatParams): ChatSession;
    // (undocumented)
    systemInstruction?: Content;
    // (undocumented)
    toolConfig?: ToolConfig;
    // (undocumented)
    tools?: Tool[];
}
```

----------------------------------------

TITLE: Defining FileDataPart Interface in TypeScript
DESCRIPTION: The TypeScript interface definition for FileDataPart in the @google/generative-ai library. It specifies a content part interface that represents FileData with a required fileData property and several optional properties marked as 'never' type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.filedatapart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileDataPart 

```

----------------------------------------

TITLE: Defining FunctionDeclaration.name Property in TypeScript
DESCRIPTION: The TypeScript signature for the name property in the FunctionDeclaration interface. This property specifies the name of the function to call and must follow specific formatting rules: it must start with a letter or underscore, contain only alphanumeric characters, underscores, or dashes, and have a maximum length of 64 characters.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclaration.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
name: string;
```

----------------------------------------

TITLE: Defining the HarmCategory Enum in Typescript
DESCRIPTION: Defines the `HarmCategory` enum, which represents different categories of harm. These categories are used in safety settings to filter or block content based on its potential for harm.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_7

LANGUAGE: typescript
CODE:
```
//@public
export enum HarmCategory {
    // (undocumented)
    HARM_CATEGORY_CIVIC_INTEGRITY = "HARM_CATEGORY_CIVIC_INTEGRITY",
    // (undocumented)
    HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT",
    // (undocumented)
    HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT",
    // (undocumented)
    HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH",
    // (undocumented)
    HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    // (undocumented)
    HARM_CATEGORY_UNSPECIFIED = "HARM_CATEGORY_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Defining FunctionCallPart Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionCallPart interface, which represents a content part for a function call. It includes optional properties like codeExecutionResult, executableCode, fileData, functionResponse, inlineData, and text, as well as a required functionCall property of type FunctionCall.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncallpart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionCallPart 
```

----------------------------------------

TITLE: Defining FileData Interface in TypeScript
DESCRIPTION: Defines the FileData interface structure used for handling file data in the Google Generative AI library. The interface includes fileUri and mimeType properties as strings.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.filedata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileData 
```

----------------------------------------

TITLE: Defining HarmBlockThreshold Enum
DESCRIPTION: This code snippet exports the HarmBlockThreshold enum which contains preset constants representing various blocking thresholds for content moderation related to harm levels. Each member of the enum defines a specific level of harm tolerance for the content, which can aid in automated filtering mechanisms.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.harmblockthreshold.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum HarmBlockThreshold {
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE",
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE",
    BLOCK_NONE = "BLOCK_NONE",
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH",
    HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Defining GroundingMetadata Interface in TypeScript
DESCRIPTION: This code snippet defines the 'GroundingMetadata' interface, outlining the structure of metadata returned when grounding is enabled. The interface includes properties like groundingChunks, groundingSupports, retrievalMetadata, searchEntryPoint, and webSearchQueries, each serving specific purposes in handling grounding data.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingmetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface GroundingMetadata 

```

----------------------------------------

TITLE: Defining SingleRequestOptions Interface in TypeScript
DESCRIPTION: TypeScript interface declaration for SingleRequestOptions that extends the RequestOptions interface. It includes an optional signal property of type AbortSignal for aborting asynchronous requests.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.singlerequestoptions.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface SingleRequestOptions extends RequestOptions 
```

----------------------------------------

TITLE: Implementing Batch Content Embedding with GenerativeModel in TypeScript
DESCRIPTION: Method signature for batchEmbedContents that processes multiple embed content requests simultaneously. Takes a BatchEmbedContentsRequest object and optional SingleRequestOptions, returning a Promise of BatchEmbedContentsResponse.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.batchembedcontents.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
batchEmbedContents(batchEmbedContentRequest: BatchEmbedContentsRequest, requestOptions?: SingleRequestOptions): Promise<BatchEmbedContentsResponse>;
```

----------------------------------------

TITLE: Defining RequestOptions Interface in TypeScript
DESCRIPTION: TypeScript interface definition for RequestOptions which contains optional configuration parameters for API requests in the Google Generative AI JavaScript SDK. It includes properties for API client identification, version selection, base URL configuration, custom headers, and request timeout settings.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.requestoptions.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface RequestOptions 

```

----------------------------------------

TITLE: Defining generationConfig Property in BaseParams Interface (TypeScript)
DESCRIPTION: Property signature definition for the generationConfig property in the BaseParams interface. This optional property accepts a GenerationConfig object that controls generation settings for AI text generation.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.baseparams.generationconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
generationConfig?: GenerationConfig;
```

----------------------------------------

TITLE: Streaming Content Generation Method Signature
DESCRIPTION: Method signature for generateContentStream() that enables streaming responses from the generative model. Takes a content request parameter and optional request options, returning a promise that resolves to a stream result object containing both the streaming iterator and final aggregated response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.generatecontentstream.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
generateContentStream(request: GenerateContentRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<GenerateContentStreamResult>;
```

----------------------------------------

TITLE: Constructing GoogleGenerativeAI Instance in TypeScript
DESCRIPTION: This snippet constructs a new instance of the `GoogleGenerativeAI` class, requiring an API key for authentication. The constructor method initializes the instance with the provided API key. There are no additional parameters or return values defined.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeai._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(apiKey: string);
```

----------------------------------------

TITLE: Declaring OpenAPI Schema Types Enumeration
DESCRIPTION: The code snippet defines an enumeration named SchemaType in TypeScript, listing various data types used in OpenAPI such as ARRAY, BOOLEAN, INTEGER, NUMBER, OBJECT, and STRING. These enumerated types help in structuring data models in OpenAPI specifications. No external dependencies are required for this enumeration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.schematype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum SchemaType
```

----------------------------------------

TITLE: Defining ErrorDetails Interface in TypeScript
DESCRIPTION: Defines the interface for error details that may be included in an error response. The interface includes optional properties for type, domain, metadata, and reason.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.errordetails.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ErrorDetails 
```

----------------------------------------

TITLE: Implementing Token Counter Method in TypeScript
DESCRIPTION: Method signature for counting tokens in provided content using Google's Generative AI model. Accepts either a CountTokensRequest object, string, or array of strings/Parts, with optional request configuration. Returns a Promise containing the token count response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.counttokens.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
countTokens(request: CountTokensRequest | string | Array<string | Part>, requestOptions?: SingleRequestOptions): Promise<CountTokensResponse>;
```

----------------------------------------

TITLE: Defining GroundingSupport Interface
DESCRIPTION: This snippet declares the GroundingSupport interface, which is used to represent grounding support in the generative AI library. It includes optional properties related to confidence scores and grounding chunk indices. The interface aids in structuring the data related to grounding support effectively in TypeScript.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingsupport.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface GroundingSupport {
}
```

----------------------------------------

TITLE: Defining SchemaType Enum in TypeScript
DESCRIPTION: This code snippet defines the SchemaType enum, which contains the list of OpenAPI data types as specified by the Swagger documentation. It includes six enum members representing different data types.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.schematype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum SchemaType 
{
  ARRAY = "array",
  BOOLEAN = "boolean",
  INTEGER = "integer",
  NUMBER = "number",
  OBJECT = "object",
  STRING = "string"
}
```

----------------------------------------

TITLE: Defining FunctionCallingMode Enum in TypeScript
DESCRIPTION: Declaration of the FunctionCallingMode enum which specifies the available modes for function calling in the Google Generative AI API. The enum includes options for AUTO, ANY, NONE, and MODE_UNSPECIFIED.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncallingmode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum FunctionCallingMode 
```

----------------------------------------

TITLE: Defining ErrorDetails Interface in TypeScript for Google Generative AI
DESCRIPTION: TypeScript interface definition for the ErrorDetails object that may be included in error responses from the Google Generative AI API. It contains optional properties for type information, domain, metadata, and reason for the error.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.errordetails.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ErrorDetails 

```

----------------------------------------

TITLE: Defining GroundingSupportSegment Interface
DESCRIPTION: This TypeScript code declares the GroundingSupportSegment interface, which serves as a model for content segments used in generative AI. It includes optional properties that define the start and end indices within a part, the part index, and the text content relevant to the segment.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingsupportsegment.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface GroundingSupportSegment 

```

----------------------------------------

TITLE: Defining the GoogleGenerativeAIError Class in Typescript
DESCRIPTION: Defines the base `GoogleGenerativeAIError` class, which extends the standard `Error` class. It serves as the parent class for more specific error types within the library, providing a consistent way to handle errors.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_5

LANGUAGE: typescript
CODE:
```
//@public
export class GoogleGenerativeAIError extends Error {
    constructor(message: string);
}
```

----------------------------------------

TITLE: Defining FunctionDeclarationSchemaProperty Type in TypeScript
DESCRIPTION: Declares a type alias FunctionDeclarationSchemaProperty that references the Schema type. Used for defining the schema structure of top-level function declarations in the Google Generative AI JavaScript library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclarationschemaproperty.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type FunctionDeclarationSchemaProperty = Schema;
```

----------------------------------------

TITLE: Defining allowedFunctionNames Property in FunctionCallingConfig Interface
DESCRIPTION: This code snippet shows the TypeScript signature for the allowedFunctionNames property. It is an optional array of strings that likely specifies which function names are allowed to be called within the configuration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncallingconfig.allowedfunctionnames.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
allowedFunctionNames?: string[];
```

----------------------------------------

TITLE: Defining the Part type in TypeScript
DESCRIPTION: This code snippet defines the `Part` type as a union of several other types, including `TextPart`, `InlineDataPart`, `FunctionCallPart`, `FunctionResponsePart`, `FileDataPart`, `ExecutableCodePart`, and `CodeExecutionResultPart`. This allows a `Part` to represent different kinds of content that can be used within a generative AI model. The type is exported for use in other modules.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.part.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type Part = TextPart | InlineDataPart | FunctionCallPart | FunctionResponsePart | FileDataPart | ExecutableCodePart | CodeExecutionResultPart;
```

----------------------------------------

TITLE: GroundingSupport Properties Table
DESCRIPTION: This snippet provides a summary of properties included in the GroundingSupport interface, detailing their types, modifiers, and descriptions. Notably, properties like confidenceScores and groundingChunkIndices help in assessing the reliability and attribution of claims made by the AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingsupport.md#2025-04-21_snippet_1

LANGUAGE: typescript
CODE:
```
|  Property | Modifiers | Type | Description |
|  --- | --- | --- | --- |
|  [confidenceScores?](./generative-ai.groundingsupport.confidencescores.md) |  | number\[\] | _(Optional)_ Confidence score of the support references. Ranges from 0 to 1. 1 is the most confident. This list must have the same size as the grounding_chunk_indices. |
|  [groundingChunckIndices?](./generative-ai.groundingsupport.groundingchunckindices.md) |  | number\[\] | _(Optional)_ A list of indices (into 'grounding_chunk') specifying the citations associated with the claim. For instance \[1,3,4\] means that grounding_chunk\[1\], grounding_chunk\[3\], grounding_chunk\[4\] are the retrieved content attributed to the claim. |
|  [segment?](./generative-ai.groundingsupport.segment.md) |  | string | _(Optional)_ URI reference of the chunk. |
```

----------------------------------------

TITLE: Defining FunctionCallingConfig Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionCallingConfig interface, which includes optional properties for specifying allowed function names and the function calling mode.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncallingconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionCallingConfig {
    allowedFunctionNames?: string[];
    mode?: FunctionCallingMode;
}
```

----------------------------------------

TITLE: Defining BatchEmbedContentsRequest Interface in TypeScript
DESCRIPTION: This code snippet defines the BatchEmbedContentsRequest interface, which is used as parameters for the GenerativeModel.batchEmbedContents() method. It contains a single property 'requests' of type EmbedContentRequest[].
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.batchembedcontentsrequest.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface BatchEmbedContentsRequest 
{
    requests: EmbedContentRequest[];
}
```

----------------------------------------

TITLE: SimpleStringSchema Interface Definition in TypeScript
DESCRIPTION: TypeScript interface definition for SimpleStringSchema which extends BaseSchema. It represents a simple string schema that may optionally include format specifications.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.simplestringschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface SimpleStringSchema extends BaseSchema 
```

----------------------------------------

TITLE: Defining FunctionDeclaration Interface in TypeScript
DESCRIPTION: Interface declaration for FunctionDeclaration type that includes optional description, required name, and optional parameters properties following OpenAPI 3.0 specification.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclaration.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface FunctionDeclaration
```

----------------------------------------

TITLE: Defining Text Part Interface
DESCRIPTION: This interface defines the structure for a text part of content. It includes a `text` property, which is a string, and other properties that are set to `never`.  This likely means only text is expected in this specific implementation.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_17

LANGUAGE: typescript
CODE:
```
export interface TextPart {
    // (undocumented)
    codeExecutionResult?: never;
    // (undocumented)
    executableCode?: never;
    // (undocumented)
    fileData?: never;
    // (undocumented)
    functionCall?: never;
    // (undocumented)
    functionResponse?: never;
    // (undocumented)
    inlineData?: never;
    // (undocumented)
    text: string;
}
```

----------------------------------------

TITLE: Defining GoogleGenerativeAIResponseError Class in TypeScript
DESCRIPTION: This snippet defines the GoogleGenerativeAIResponseError class, which extends GoogleGenerativeAIError. It is used for errors in the contents of a response from the model, including parsing errors or responses with safety block reasons.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeairesponseerror.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleGenerativeAIResponseError<T> extends GoogleGenerativeAIError 
```

----------------------------------------

TITLE: ArraySchema Interface Definition in TypeScript
DESCRIPTION: Defines the ArraySchema interface that extends BaseSchema to describe an ordered list of values. It includes properties for specifying the schema of array items and constraints on array length.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.arrayschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ArraySchema extends BaseSchema 

```

----------------------------------------

TITLE: Defining Custom Headers Property for HTTP Requests - Typescript
DESCRIPTION: This TypeScript snippet defines the optional 'customHeaders' property in the RequestOptions interface, allowing users to specify custom HTTP request headers. This property can either be a 'Headers' object or a record of key-value pairs where both key and value are strings. There are no additional dependencies required for this snippet as it uses basic TypeScript types. This functionality is crucial for customizing headers in outgoing HTTP requests and extracting headers from incoming responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.requestoptions.customheaders.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
customHeaders?: Headers | Record<string, string>;
```

----------------------------------------

TITLE: Defining ResponseMimeType Property in GenerationConfig
DESCRIPTION: TypeScript property definition for responseMimeType that specifies the output format of generated responses. Supports 'text/plain' (default) for text output and 'application/json' for JSON responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.responsemimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
responseMimeType?: string;
```

----------------------------------------

TITLE: Defining toolConfig Property in CachedContentBase Class (TypeScript)
DESCRIPTION: This code snippet defines the toolConfig property for the CachedContentBase class. It is an optional property of type ToolConfig.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentbase.toolconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
toolConfig?: ToolConfig;
```

----------------------------------------

TITLE: Defining StringSchema Union Type in TypeScript
DESCRIPTION: This code defines a TypeScript type alias named StringSchema which is a union of SimpleStringSchema and EnumStringSchema types. This type is used to describe string values in the Google Generative AI library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.stringschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type StringSchema = SimpleStringSchema | EnumStringSchema;
```

----------------------------------------

TITLE: NumberSchema Interface Definition
DESCRIPTION: Defines the NumberSchema interface, which extends BaseSchema and describes a JSON-encodable floating-point number.  It includes properties for specifying the number's format (optional) and type.  The type property is a reference to SchemaType.NUMBER.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.numberschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface NumberSchema extends BaseSchema 
```

----------------------------------------

TITLE: Defining Tool Configuration Interface in TypeScript
DESCRIPTION: This TypeScript interface 'ToolConfig' defines configuration settings shared across tools in a request within the generative AI framework. It requires no specific dependencies, outside of its integration within the 'generative-ai' package, and is meant to standardize configuration parameters. There are no parameters taken directly by this interface as it serves as a structural definition. Its intended use is during the initialization of tools.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.toolconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ToolConfig 
```

----------------------------------------

TITLE: Defining UsageMetadata Property Type in GenerateContentResponse
DESCRIPTION: TypeScript property definition that specifies an optional UsageMetadata type which contains information about token usage for content generation requests.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentresponse.usagemetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
usageMetadata?: UsageMetadata;
```

----------------------------------------

TITLE: Defining CodeExecutionTool TypeScript Interface
DESCRIPTION: Declares an interface that allows code execution functionality in the generative AI model, with a flexible configuration for future extensions
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.codeexecutiontool.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CodeExecutionTool {
  codeExecution: {}
}
```

----------------------------------------

TITLE: Exporting SimpleStringSchema Interface in TypeScript
DESCRIPTION: Defines an interface named SimpleStringSchema which extends BaseSchema. This interface describes a schema for simple strings with optional properties like format and enumeration, aimed at representing structured data in generative AI contexts. The type is intended to provide a foundation for specifying string-based data with potential date-time format support.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.simplestringschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface SimpleStringSchema extends BaseSchema
```

----------------------------------------

TITLE: Defining SystemInstruction Property Type in TypeScript
DESCRIPTION: Type definition for the systemInstruction property that can accept a string, Part, or Content type. This property is optional as indicated by the '?' modifier.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentrequest.systeminstruction.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
systemInstruction?: string | Part | Content;
```

----------------------------------------

TITLE: Defining candidateCount Property in GenerationConfig Interface (TypeScript)
DESCRIPTION: The signature for the candidateCount optional property in the GenerationConfig interface. This property determines the number of candidate responses to generate for each prompt.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.candidatecount.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
candidateCount?: number;
```

----------------------------------------

TITLE: Defining LogprobsResult Interface TypeScript
DESCRIPTION: The purpose of this snippet is to declare the LogprobsResult interface within the @google/generative-ai package, which captures potential results in generative AI models' log probability decoding steps. The snippet outlines properties like chosenCandidates and topCandidates that represent the path and best candidates in decoding, with arrays indicating the number of decoding steps. Considering TypeScript, it assumes familiarity with interface declaration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.logprobsresult.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
export interface LogprobsResult 
```

----------------------------------------

TITLE: Defining GenerationConfig Property in GenerativeModel Class (TypeScript)
DESCRIPTION: This snippet shows the TypeScript signature for the generationConfig property of the GenerativeModel class. The property is of type GenerationConfig, which likely contains configuration settings for generating content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.generationconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
generationConfig: GenerationConfig;
```

----------------------------------------

TITLE: Defining the ToolConfig Interface - TypeScript
DESCRIPTION: This code snippet defines the ToolConfig interface, which serves as a configuration structure for tools in the Google generative AI framework. It outlines potential properties and types that can be used to configure function calling within tools.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.toolconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ToolConfig 

```

----------------------------------------

TITLE: Retrieving Cached Content with GoogleAICacheManager in TypeScript
DESCRIPTION: This method retrieves a content cache by name. It takes a string parameter 'name' and returns a Promise that resolves to a CachedContent object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager.get.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
get(name: string): Promise<CachedContent>;
```

----------------------------------------

TITLE: Defining Outcome Enum in TypeScript
DESCRIPTION: An enumeration that represents different possible outcomes of code execution, including success, failure, timeout, and unspecified states. Used for tracking and reporting code execution results.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.outcome.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum Outcome {
  OUTCOME_DEADLINE_EXCEEDED = "outcome_deadline_exceeded",
  OUTCOME_FAILED = "outcome_failed",
  OUTCOME_OK = "outcome_ok",
  OUTCOME_UNSPECIFIED = "outcome_unspecified"
}
```

----------------------------------------

TITLE: InlineDataPart Interface Definition
DESCRIPTION: Defines the structure of the `InlineDataPart` interface. This interface is designed to represent a content part that contains inline data, such as an image. The interface includes optional properties for different data types, ensuring flexibility in representing various content formats.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.inlinedatapart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface InlineDataPart 
```

----------------------------------------

TITLE: Exporting IntegerSchema Interface in TypeScript
DESCRIPTION: Defines the IntegerSchema interface which encapsulates a JSON-encodable integer. This interface extends BaseSchema and includes properties for defining the format (such as 'int32' or 'int64') and the type as SchemaType.INTEGER. This snippet is part of the generative AI library and requires the base schema to be defined.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.integerschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface IntegerSchema extends BaseSchema
```

----------------------------------------

TITLE: ContentEmbedding Interface Definition
DESCRIPTION: This TypeScript interface defines the structure of a content embedding. It includes a single property, `values`, which is an array of numbers representing the embedding vector. This interface is part of the `@google/generative-ai` package.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.contentembedding.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ContentEmbedding 
```

----------------------------------------

TITLE: Defining GenerativeModel.cachedContent Property Type in TypeScript
DESCRIPTION: Type definition showing the signature of the cachedContent property which is of type CachedContent.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.cachedcontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
cachedContent: CachedContent;
```

----------------------------------------

TITLE: Defining Temperature Property in GenerationConfig
DESCRIPTION: TypeScript type definition for the optional temperature property that controls randomness in model generation. The temperature is specified as a number value.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.temperature.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
temperature?: number;
```

----------------------------------------

TITLE: Defining ListFilesResponse.files Property Type in TypeScript
DESCRIPTION: Type definition for the files property in the ListFilesResponse interface. The property is an array of FileMetadataResponse objects that contains metadata about files.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.listfilesresponse.files.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
files: FileMetadataResponse[];
```

----------------------------------------

TITLE: Initializing GoogleAIFileManager Constructor - TypeScript
DESCRIPTION: Constructor signature for creating a new instance of the GoogleAIFileManager class. Takes an API key as a required parameter and optional request options.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(apiKey: string, _requestOptions?: RequestOptions);
```

----------------------------------------

TITLE: Defining Base URL in TypeScript
DESCRIPTION: This TypeScript snippet defines a 'baseUrl' property for managing the endpoint URL in request options. The property can be a string and defaults to 'https://generativelanguage.googleapis.com', providing a base endpoint for the Generative AI API if not specified otherwise. This setup allows for flexible configuration of API requests while providing a sensible default.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.requestoptions.baseurl.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
baseUrl?: string;
```

----------------------------------------

TITLE: Declaring GoogleGenerativeAIRequestInputError Class in TypeScript
DESCRIPTION: This snippet defines the GoogleGenerativeAIRequestInputError class, which extends GoogleGenerativeAIError. It is used to represent errors in the contents of a request originating from user input when interacting with the Google Generative AI API.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeairequestinputerror.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleGenerativeAIRequestInputError extends GoogleGenerativeAIError 
```

----------------------------------------

TITLE: Defining RetrievalMetadata Interface in TypeScript
DESCRIPTION: Declaration of the RetrievalMetadata interface which contains metadata related to retrieval in the grounding flow. This interface is exported from the @google/generative-ai package.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.retrievalmetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface RetrievalMetadata 
```

----------------------------------------

TITLE: Defining Object Properties Structure in TypeScript
DESCRIPTION: This code snippet defines a structure for JSON object properties within the @google/generative-ai namespace. It uses a dictionary pattern where each key represents a string and is associated with a Schema type, ensuring each object's properties are non-empty and well-defined. Dependencies include the TypeScript language and an assumed definition for Schema.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.objectschema.properties.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
properties: {
        [k: string]: Schema;
    };
```

----------------------------------------

TITLE: Defining stopSequences Property in GenerationConfig Interface in TypeScript
DESCRIPTION: TypeScript signature for the stopSequences property in the GenerationConfig interface. This optional property accepts an array of strings that define sequences at which text generation should stop.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.stopsequences.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
stopSequences?: string[];
```

----------------------------------------

TITLE: Defining BatchEmbedContentsResponse Embeddings Array
DESCRIPTION: A TypeScript property that represents an array of ContentEmbedding objects, typically used to store embedding results for multiple content items in a batch processing scenario
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.batchembedcontentsresponse.embeddings.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
embeddings: ContentEmbedding[];
```

----------------------------------------

TITLE: Defining FunctionDeclarationsTool Interface in TypeScript
DESCRIPTION: The TypeScript interface definition for FunctionDeclarationsTool, which enables interaction with external systems to perform actions outside the model's knowledge and scope.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclarationstool.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface FunctionDeclarationsTool 
```

----------------------------------------

TITLE: Defining responseSchema Property in TypeScript for GenerationConfig
DESCRIPTION: TypeScript signature for the responseSchema property in the GenerationConfig class. This property allows specifying an output response schema when the responseMIMEType is set to application/json.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.responseschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
responseSchema?: ResponseSchema;
```

----------------------------------------

TITLE: Declaring SafetySettings Property in TypeScript
DESCRIPTION: Type definition for the safetySettings property that specifies an array of SafetySetting objects used to configure model safety parameters.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.safetysettings.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
safetySettings: SafetySetting[];
```

----------------------------------------

TITLE: Defining mimeType Property in FileMetadata Interface in TypeScript
DESCRIPTION: Property signature for the mimeType field in the FileMetadata interface. This property specifies the MIME type of a file as a string value when working with file operations in the Google Generative AI SDK.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadata.mimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mimeType: string;
```

----------------------------------------

TITLE: Defining Task Type Enum
DESCRIPTION: This enum defines the possible task types for a model. It includes values like CLASSIFICATION, CLUSTERING, RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, SEMANTIC_SIMILARITY, and TASK_TYPE_UNSPECIFIED.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_16

LANGUAGE: typescript
CODE:
```
export enum TaskType {
    // (undocumented)
    CLASSIFICATION = "CLASSIFICATION",
    // (undocumented)
    CLUSTERING = "CLUSTERING",
    // (undocumented)
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT",
    // (undocumented)
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY",
    // (undocumented)
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY",
    // (undocumented)
    TASK_TYPE_UNSPECIFIED = "TASK_TYPE_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Defining AbortSignal Property in SingleRequestOptions Interface (TypeScript)
DESCRIPTION: This code snippet defines the 'signal' property in the SingleRequestOptions interface. It is an optional property of type AbortSignal, used for aborting asynchronous requests. The property can be used to cancel operations, but it's important to note that this cancellation only occurs client-side and does not affect the service-side execution or billing.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.singlerequestoptions.signal.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
signal?: AbortSignal;
```

----------------------------------------

TITLE: CachedContentBase Interface Definition
DESCRIPTION: Defines the structure of the `CachedContentBase` interface.  This interface is used to represent the base structure of cached content with properties for content, display name, expiration time, model, system instruction, tool configuration, and tools.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentbase.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CachedContentBase 
```

----------------------------------------

TITLE: Listing Uploaded Files - TypeScript
DESCRIPTION: This method lists all uploaded files using optional parameters to modify the request. The method returns a promise that resolves to a ListFilesResponse. It accepts optional parameters for list specifications and request options that can override default settings.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager.listfiles.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
listFiles(listParams?: ListParams, requestOptions?: SingleRequestOptions): Promise<ListFilesResponse>;
```

----------------------------------------

TITLE: Defining FunctionCall.args Property in TypeScript
DESCRIPTION: TypeScript signature for the 'args' property in the 'FunctionCall' class. This property takes an object type that likely contains the arguments for a function call.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncall.args.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
args: object;
```

----------------------------------------

TITLE: Defining Optional Required Parameters Array in TypeScript
DESCRIPTION: This TypeScript signature defines an optional property 'required' that accepts an array of strings. The property is used to specify which parameters are required when declaring functions in the Generative AI framework.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclarationschema.required.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
required?: string[];
```

----------------------------------------

TITLE: Defining topK Property in GenerationConfig TypeScript Interface
DESCRIPTION: TypeScript signature for the optional topK property in the GenerationConfig class. The topK parameter controls top-K sampling, which limits token selection to the K most likely next tokens.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.topk.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
topK?: number;
```

----------------------------------------

TITLE: Defining logprobsResult Property in GenerateContentCandidate Class - TypeScript
DESCRIPTION: This code snippet defines the logprobsResult property in the GenerateContentCandidate class. It is an optional property of type LogprobsResult, which contains log-likelihood scores for the response tokens and top tokens.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentcandidate.logprobsresult.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
logprobsResult?: LogprobsResult;
```

----------------------------------------

TITLE: Defining the Dynamic Retrieval Configuration Interface in TypeScript
DESCRIPTION: The code snippet declares the 'DynamicRetrievalConfig' interface, which is part of the generative AI library and specifies the dynamic retrieval configurations. There are optional properties such as 'dynamicThreshold', a numeric value that determines the threshold for retrieval, and 'mode', which determines the mode of dynamic retrieval. This interface facilitates customizing retrieval behaviors in generative AI applications. No explicit dependencies are required for this snippet.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.dynamicretrievalconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface DynamicRetrievalConfig
```

----------------------------------------

TITLE: Defining FileDataPart.fileData Property in TypeScript
DESCRIPTION: Declaration of the fileData property within the FileDataPart class. This property has a type of FileData and likely stores file content for processing by the generative AI services.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.filedatapart.filedata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
fileData: FileData;
```

----------------------------------------

TITLE: Declaring mimeType Property in FileMetadataResponse Class in TypeScript
DESCRIPTION: TypeScript signature for the mimeType property which is a string field in the FileMetadataResponse class. This property likely stores the MIME type of a file processed by the Generative AI API.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadataresponse.mimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mimeType: string;
```

----------------------------------------

TITLE: Defining TextPart Interface in Typescript
DESCRIPTION: This code defines the `TextPart` interface using TypeScript.  It specifies the structure for representing a text string within the generative AI content. The interface includes a required `text` property of type string, and several optional properties that are set to `never`, indicating they're not applicable to TextPart.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.textpart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface TextPart 
```

----------------------------------------

TITLE: Retrieving File Metadata using GoogleAIFileManager in TypeScript
DESCRIPTION: The getFile method retrieves metadata for a specified file using its ID in a TypeScript application. It accepts a file ID as a string and an optional requestOptions object of SingleRequestOptions type. This allows the user to specify request parameters overriding the default RequestOptions set during GoogleAIFileManager initialization. It returns a promise that resolves with a FileMetadataResponse object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager.getfile.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
getFile(fileId: string, requestOptions?: SingleRequestOptions): Promise<FileMetadataResponse>;
```

----------------------------------------

TITLE: Defining GoogleGenerativeAIFetchError Class in TypeScript
DESCRIPTION: This code snippet defines the GoogleGenerativeAIFetchError class, which extends GoogleGenerativeAIError. It is used to handle HTTP errors when calling the server, including HTTP status, statusText, and optional error details from the server response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeaifetcherror.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleGenerativeAIFetchError extends GoogleGenerativeAIError 
```

----------------------------------------

TITLE: Defining SafetySetting.threshold Property in TypeScript
DESCRIPTION: This code snippet defines the 'threshold' property for the SafetySetting interface. It specifies that the property is of type HarmBlockThreshold, which likely represents different levels of safety thresholds for content filtering or blocking.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.safetysetting.threshold.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
threshold: HarmBlockThreshold;
```

----------------------------------------

TITLE: Defining FunctionDeclaration.parameters Property in TypeScript
DESCRIPTION: TypeScript signature for the 'parameters' property in the FunctionDeclaration interface. This optional property uses the FunctionDeclarationSchema type to define function parameters in JSON Schema Object format following Open API 3.03.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclaration.parameters.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
parameters?: FunctionDeclarationSchema;
```

----------------------------------------

TITLE: Defining ExecutableCode.language Property in TypeScript
DESCRIPTION: Declares the 'language' property of the ExecutableCode interface. It is of type ExecutableCodeLanguage, which likely represents an enum or union type of supported programming languages.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecode.language.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
language: ExecutableCodeLanguage;
```

----------------------------------------

TITLE: Defining Top Candidates Array in TypeScript
DESCRIPTION: This TypeScript snippet defines the topCandidates property, which is an array of TopCandidates objects. It is a part of the LogprobsResult interface within a generative AI module. The property is intended to hold candidates generated during the decoding process, where the length of the array corresponds to the total number of decoding steps. The TopCandidates refers to an array of objects representing individual decoding steps.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.logprobsresult.topcandidates.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
topCandidates: TopCandidates[];
```

----------------------------------------

TITLE: Defining Tool Type Alias
DESCRIPTION: This type alias defines `Tool` as one of the allowed tool types: FunctionDeclarationsTool, CodeExecutionTool, or GoogleSearchRetrievalTool.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_18

LANGUAGE: typescript
CODE:
```
export type Tool = FunctionDeclarationsTool | CodeExecutionTool | GoogleSearchRetrievalTool;
```

----------------------------------------

TITLE: Defining customHeaders property in TypeScript
DESCRIPTION: The `customHeaders` property allows setting custom HTTP request headers. It accepts either a `Headers` object or a simple record (object) where keys and values are strings. This provides flexibility in how headers are specified.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.requestoptions.customheaders.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
customHeaders?: Headers | Record<string, string>;
```
```

----------------------------------------

TITLE: Defining ExecutableCodeLanguage Enum in TypeScript
DESCRIPTION: This enum defines the supported executable code languages for the generative AI API. It includes options for unspecified language and Python.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecodelanguage.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum ExecutableCodeLanguage 
{
  LANGUAGE_UNSPECIFIED = "language_unspecified",
  PYTHON = "python"
}
```

----------------------------------------

TITLE: Defining the params Property in ChatSession Class with TypeScript
DESCRIPTION: Signature definition for the optional params property in the ChatSession class. This property is of type StartChatParams and is used to configure a chat session.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession.params.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
params?: StartChatParams;
```

----------------------------------------

TITLE: Defining ArraySchema Interface in TypeScript
DESCRIPTION: This code snippet defines the ArraySchema interface, which extends BaseSchema. It includes properties for specifying the schema of array items, maximum and minimum number of items, and the type of the schema.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.arrayschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ArraySchema extends BaseSchema 
{
  items: Schema;
  maxItems?: number;
  minItems?: number;
  type: typeof SchemaType.ARRAY;
}
```

----------------------------------------

TITLE: Defining CachedContent Interface in TypeScript
DESCRIPTION: This code snippet defines the CachedContent interface, which extends CachedContentBase. It includes optional properties for creation time, name, TTL, and update time.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.cachedcontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CachedContent extends CachedContentBase 
{
    createTime?: string;
    name?: string;
    ttl?: string;
    updateTime?: string;
}
```

----------------------------------------

TITLE: Defining Optional SystemInstruction in TypeScript
DESCRIPTION: Declares a system instruction property with multiple possible type definitions, allowing flexibility in specifying model instructions
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.modelparams.systeminstruction.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
systemInstruction?: string | Part | Content;
```

----------------------------------------

TITLE: Defining Base URL in TypeScript
DESCRIPTION: This snippet defines an optional base URL property for request options in the Google Generative AI framework. The base URL defaults to 'https://generativelanguage.googleapis.com', allowing users to specify a different endpoint if needed. The property is declared as an optional string to accommodate various use cases.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.requestoptions.baseurl.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
baseUrl?: string;
```

----------------------------------------

TITLE: Defining Description Property in FunctionDeclaration Interface - TypeScript
DESCRIPTION: TypeScript interface property definition for an optional description field that provides information about the function's purpose. This description helps the AI model determine when and how to call the function.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclaration.description.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
description?: string;
```

----------------------------------------

TITLE: Defining Content Property
DESCRIPTION: This snippet defines a property named 'content' in the EmbedContentRequest type, specifying that it should adhere to the Content interface/type. This is crucial for ensuring type safety and clarity in the use of embedded content within generative AI requests.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.embedcontentrequest.content.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
content: Content;
```

----------------------------------------

TITLE: Defining FunctionCall.name Property in TypeScript
DESCRIPTION: This code snippet defines the 'name' property of the FunctionCall interface. It specifies that 'name' is a string type, which likely represents the name of the function being called.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncall.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
name: string;
```

----------------------------------------

TITLE: TopCandidates candidates property definition in TypeScript
DESCRIPTION: This snippet shows the definition of the `candidates` property within the `TopCandidates` class. The `candidates` property is an array of `LogprobsCandidate` objects. These candidates are sorted by their log probability in descending order, indicating the most likely candidates are listed first.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.topcandidates.candidates.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
candidates: LogprobsCandidate[];
```
```

----------------------------------------

TITLE: Declaring FunctionCallingConfig Mode Property in TypeScript
DESCRIPTION: Type definition for the optional mode property that accepts a FunctionCallingMode value within the FunctionCallingConfig interface.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncallingconfig.mode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mode?: FunctionCallingMode;
```

----------------------------------------

TITLE: Defining CodeExecutionResult Property in TypeScript
DESCRIPTION: Declares a property of type CodeExecutionResult within the CodeExecutionResultPart interface, used for storing the outcome of code execution in the Google Generative AI library
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.codeexecutionresultpart.codeexecutionresult.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
codeExecutionResult: CodeExecutionResult;
```

----------------------------------------

TITLE: Defining SearchEntryPoint Interface in TypeScript
DESCRIPTION: Interface declaration for SearchEntryPoint that defines the structure of Google search entry points. Contains optional properties for rendered web content and base64 encoded search data.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.searchentrypoint.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface SearchEntryPoint 
```

----------------------------------------

TITLE: Gemini AI Response JSON Structure
DESCRIPTION: This JSON snippet shows the structure of a response from the Gemini AI model. It includes a list of candidate responses, each with content, a finish reason, an index, and safety ratings. It also provides feedback on the safety of the input prompt, including safety ratings.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-success-basic-reply-short.txt#2025-04-21_snippet_0

LANGUAGE: JSON
CODE:
```
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "Cheyenne"
      }]
    },
    "finishReason": "STOP",
    "index": 0,
    "safetyRatings": [{
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "probability": "NEGLIGIBLE"
    }, {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "probability": "NEGLIGIBLE"
    }, {
      "category": "HARM_CATEGORY_HARASSMENT",
      "probability": "NEGLIGIBLE"
    }, {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "probability": "NEGLIGIBLE"
    }]
  }],
  "promptFeedback": {
    "safetyRatings": [{
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "probability": "NEGLIGIBLE"
    }, {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "probability": "NEGLIGIBLE"
    }, {
      "category": "HARM_CATEGORY_HARASSMENT",
      "probability": "NEGLIGIBLE"
    }, {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "probability": "NEGLIGIBLE"
    }]
  }
}
```

----------------------------------------

TITLE: Defining Expiration Time for Cached Content in TypeScript
DESCRIPTION: This TypeScript snippet defines an optional expiration time for cached content, expressed as an ISO string. Either this property or 'ttlSeconds' should be provided when creating a 'CachedContent'. This setup allows for precise control over when cached data should be considered stale, relying on ISO 8601 string format for time representation. No external dependencies are needed besides Typescript itself.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentbase.expiretime.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
expireTime?: string;
```

----------------------------------------

TITLE: Listing Uploaded Files - TypeScript
DESCRIPTION: The listFiles method allows users to list all uploaded files. It accepts optional parameters to customize the request. The method returns a Promise that resolves to a ListFilesResponse, which contains the details of the files listed. The method considers any fields set in the optional requestOptions parameter over default requestOptions during initialization.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager.listfiles.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
listFiles(listParams?: ListParams, requestOptions?: SingleRequestOptions): Promise<ListFilesResponse>;
```

----------------------------------------

TITLE: Defining apiKey Property in GenerativeModel Class (TypeScript)
DESCRIPTION: This snippet shows the TypeScript signature for the apiKey property of the GenerativeModel class. It is defined as a string type, likely used to store the API key for authentication with the generative AI service.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.apikey.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
apiKey: string;
```

----------------------------------------

TITLE: Defining history property type in StartChatParams interface
DESCRIPTION: TypeScript type definition for the optional history property that accepts an array of Content objects used to initialize a chat session.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.startchatparams.history.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
history?: Content[];
```

----------------------------------------

TITLE: Defining ExecutableCode Property Signature in TypeScript
DESCRIPTION: Defines the executableCode property on the ExecutableCodePart interface, specifying that it contains an ExecutableCode object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecodepart.executablecode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
executableCode: ExecutableCode;
```

----------------------------------------

TITLE: Exporting CachedContentBase Interface in TypeScript
DESCRIPTION: The CachedContentBase interface serves as a blueprint for managing cached content with generative AI models. Key properties include contents (an array of Content), displayName, expireTime (in ISO format), model, systemInstruction (which can be a string, Part, or Content), toolConfig, and tools (an array of Tool). Dependencies include references to Content, Part, ToolConfig, and Tool types. Optional properties provide flexibility for specifying instructions and configurations for AI content generation.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.cachedcontentbase.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CachedContentBase
```

----------------------------------------

TITLE: Defining GenerateContentResult Interface in TypeScript
DESCRIPTION: This code snippet defines the GenerateContentResult interface, which has a single property 'response' of type EnhancedGenerateContentResponse. This interface represents the structure of the result returned by the generateContent() function.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentresult.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerateContentResult 
{
  response: EnhancedGenerateContentResponse;
}
```

----------------------------------------

TITLE: Defining EnumStringSchema enum Property Type in TypeScript
DESCRIPTION: Type definition for the enum property that specifies an array of possible string values for an enumeration. This property is used to define the valid values that can be used in an enum-type string field.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.enumstringschema.enum.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
enum: string[];
```

----------------------------------------

TITLE: Defining codeExecutionResult Property in TypeScript
DESCRIPTION: This code snippet defines the codeExecutionResult property of the CodeExecutionResultPart interface. It specifies that the property is of type CodeExecutionResult.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.codeexecutionresultpart.codeexecutionresult.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
codeExecutionResult: CodeExecutionResult;
```

----------------------------------------

TITLE: Defining Required Properties in ObjectSchema - TypeScript
DESCRIPTION: This code snippet declares the 'required' property for an ObjectSchema in TypeScript. It indicates that the required property is an optional array of strings, each representing a key that must be present in the generated object. This ensures that developers know which properties are essential for the schema's functionality.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.objectschema.required.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
required?: string[];
```

----------------------------------------

TITLE: Parsing Gemini AI Safety Ratings in JSON
DESCRIPTION: Represents a Gemini AI response with candidate content, safety ratings, and prompt feedback. Includes safety probability assessments for different harm categories.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-failure-finish-reason-safety.txt#2025-04-21_snippet_0

LANGUAGE: json
CODE:
```
{
  "candidates": [{
    "content": {"parts": [{"text": "No"}]},
    "finishReason": "SAFETY",
    "index": 0,
    "safetyRatings": [
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
      {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "HIGH"},
      {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
    ]
  }],
  "promptFeedback": {
    "safetyRatings": [
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
      {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
      {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
    ]
  }
}
```

----------------------------------------

TITLE: Defining expireTime Property in CachedContentUpdateInputFields Interface (TypeScript)
DESCRIPTION: This code snippet defines the expireTime property as an optional string within the CachedContentUpdateInputFields interface. It represents the expiration time for cached content updates.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentupdateinputfields.expiretime.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
expireTime?: string;
```

----------------------------------------

TITLE: Defining safetySettings Property in TypeScript
DESCRIPTION: Declares the safetySettings property as an optional array of SafetySetting objects within the BaseParams interface. This property allows configuration of safety settings for the generative AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.baseparams.safetysettings.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
safetySettings?: SafetySetting[];
```

----------------------------------------

TITLE: Constructing GoogleGenerativeAIFetchError Class - TypeScript
DESCRIPTION: This TypeScript constructor initializes a new instance of the GoogleGenerativeAIFetchError class. It accepts a message parameter, and optionally accepts status, statusText, and errorDetails to provide more context about the error. The errorDetails parameter is an array of ErrorDetails objects.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeaifetcherror._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(message: string, status?: number, statusText?: string, errorDetails?: ErrorDetails[]);
```

----------------------------------------

TITLE: Defining GenerateContentResponse.promptFeedback Property Type in TypeScript
DESCRIPTION: TypeScript type definition for the promptFeedback optional property that returns PromptFeedback related to content filtering results.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentresponse.promptfeedback.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
promptFeedback?: PromptFeedback;
```

----------------------------------------

TITLE: Defining ResponseSchema Type in TypeScript
DESCRIPTION: This snippet defines the `ResponseSchema` type as an alias for the `Schema` type. It's used to specify the structure of the expected response from the Generative AI API when provided in the `GenerationConfig`. This allows for structured data extraction from the model's response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.responseschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type ResponseSchema = Schema;
```

----------------------------------------

TITLE: Defining totalTokens Property in TypeScript
DESCRIPTION: This code snippet defines the `totalTokens` property within the `CountTokensResponse` interface. The property is of type `number`, indicating that it represents a numerical value. This property likely represents the total number of tokens counted in a given text or prompt processed by the Generative AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.counttokensresponse.totaltokens.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"totalTokens: number;"
```

----------------------------------------

TITLE: Defining FileMetadataResponse Interface in TypeScript
DESCRIPTION: Type definition for the FileMetadataResponse interface which contains metadata information for a file returned from the Google Generative AI API. It includes properties for file identification, timestamps, state, and optional fields for errors and video metadata.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadataresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileMetadataResponse 
```

----------------------------------------

TITLE: Defining the apiClient Property in RequestOptions Interface using TypeScript
DESCRIPTION: This code snippet defines the optional apiClient property of the RequestOptions interface, which allows including additional attribution information in the x-goog-api-client header when using wrapper SDKs.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.requestoptions.apiclient.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
apiClient?: string;
```

----------------------------------------

TITLE: Defining maxOutputTokens Property in GenerationConfig Interface (TypeScript)
DESCRIPTION: Type definition for the optional maxOutputTokens property in the GenerationConfig interface. This property allows developers to limit the maximum number of tokens that the model can generate in its response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.maxoutputtokens.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
maxOutputTokens?: number;
```

----------------------------------------

TITLE: Defining Usage Metadata Interface
DESCRIPTION: This interface defines the structure for usage metadata, including token counts for cached content, candidates, prompt, and total count.  The `cachedContentTokenCount` is optional, while the other three are required numbers.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_21

LANGUAGE: typescript
CODE:
```
export interface UsageMetadata {
    cachedContentTokenCount?: number;
    candidatesTokenCount: number;
    promptTokenCount: number;
    totalTokenCount: number;
}
```

----------------------------------------

TITLE: Retrieving Stock Price Data in JSON
DESCRIPTION: This snippet contains a JSON object that encapsulates the candidates' responses with the text representation of the current stock price of Alphabet Inc. It includes metadata about token counts used in the inquiry.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-success-search-grounding.txt#2025-04-21_snippet_0

LANGUAGE: json
CODE:
```
data: {"candidates": [{"content": {"parts": [{"text": "The"}], "role": "model"}, "finishReason": "STOP", "index": 0}], "usageMetadata": {"promptTokenCount": 8, "candidatesTokenCount": 1, "totalTokenCount": 9}}
```

----------------------------------------

TITLE: Defining mimeType Property in FileMetadataResponse Class in TypeScript
DESCRIPTION: TypeScript signature for the mimeType property of the FileMetadataResponse class. This property stores the MIME type of a file as a string value.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadataresponse.mimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mimeType: string;
```

----------------------------------------

TITLE: Deleting Files with GoogleAIFileManager in TypeScript
DESCRIPTION: Method signature for deleting a file using its ID. Takes a required fileId parameter as string and optional requestOptions parameter for customizing the request behavior. Returns a Promise that resolves to void when deletion is complete.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager.deletefile.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
deleteFile(fileId: string, requestOptions?: SingleRequestOptions): Promise<void>;
```

----------------------------------------

TITLE: Defining Content.role Property in TypeScript
DESCRIPTION: This snippet defines the role property of the Content object as a string type. It is part of a larger API documentation generated for the Google Gemini project, specifically for the generative AI library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.content.role.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
role: string;
```

----------------------------------------

TITLE: Defining Top Candidates Interface
DESCRIPTION: This interface defines the structure for top candidate results, including an array of `LogprobsCandidate` objects stored in the `candidates` property.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_20

LANGUAGE: typescript
CODE:
```
export interface TopCandidates {
    candidates: LogprobsCandidate[];
}
```

----------------------------------------

TITLE: Initializing GoogleAIFileManager TypeScript Class
DESCRIPTION: Defines the GoogleAIFileManager class for handling file operations with GoogleAI, including constructor with API key and request options
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleAIFileManager
```

----------------------------------------

TITLE: Uploading Files with GoogleAIFileManager in TypeScript
DESCRIPTION: This method allows uploading a file to the Google AI service. It takes file data as either a string or Buffer, along with file metadata, and returns a Promise that resolves to an UploadFileResponse.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager.uploadfile.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
uploadFile(fileData: string | Buffer, fileMetadata: FileMetadata): Promise<UploadFileResponse>;
```

----------------------------------------

TITLE: Defining FunctionCall.name Property in TypeScript
DESCRIPTION: This code snippet shows the TypeScript signature for the 'name' property of the FunctionCall class. The property is of type string and is likely used to store the name of the function being called.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncall.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
name: string;
```

----------------------------------------

TITLE: Declaring Optional Task Type for Content Embedding
DESCRIPTION: Defines an optional TaskType property in the EmbedContentRequest interface, allowing specification of the semantic context or purpose of the content being embedded
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.embedcontentrequest.tasktype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
taskType?: TaskType;
```

----------------------------------------

TITLE: Defining FileDataPart Interface in TypeScript
DESCRIPTION: The `FileDataPart` interface represents a component of a file's data within the Google Gemini generative AI framework. This interface includes optional properties such as code execution results and executable code, as well as mandatory file data properties. The properties are primarily links to additional documentation for further details.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filedatapart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileDataPart 
```

----------------------------------------

TITLE: Defining Custom Headers in TypeScript
DESCRIPTION: This code snippet defines the optional 'customHeaders' property in the RequestOptions interface for making HTTP requests. It can be either a Headers object or a Record of string pairs, allowing flexibility in how custom headers are specified for requests.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.requestoptions.customheaders.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
customHeaders?: Headers | Record<string, string>;
```

----------------------------------------

TITLE: Defining FileMetadataResponse Expiration Time in TypeScript
DESCRIPTION: A string property that represents the expiration time for file metadata in a strongly typed TypeScript interface or class
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadataresponse.expirationtime.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
expirationTime: string;
```

----------------------------------------

TITLE: Defining PromptFeedback Interface
DESCRIPTION: This snippet exports the PromptFeedback interface which includes properties related to prompt feedback management in the generative AI framework. It includes mandatory and optional properties for handling blocking reasons and associated safety ratings. The interface is essential for type safety within TypeScript applications utilizing the generative AI library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.promptfeedback.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface PromptFeedback \n
```

----------------------------------------

TITLE: Retrieving File Metadata with GoogleAIFileManager in TypeScript
DESCRIPTION: This method retrieves metadata for a file using its ID. The optional requestOptions parameter allows overriding the default RequestOptions values set during GoogleAIFileManager initialization.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager.getfile.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
getFile(fileId: string, requestOptions?: SingleRequestOptions): Promise<FileMetadataResponse>;
```

----------------------------------------

TITLE: Defining responseLogprobs Property in GenerationConfig Interface (TypeScript)
DESCRIPTION: This code snippet defines the responseLogprobs property in the GenerationConfig interface. It is an optional boolean property that, when set to true, indicates that the logprobs results should be exported in the response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.responselogprobs.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
responseLogprobs?: boolean;
```

----------------------------------------

TITLE: Defining chosenCandidates Property in TypeScript
DESCRIPTION: This code snippet defines the chosenCandidates property of the LogprobsResult object as an array of LogprobsCandidate objects. It specifies that the length of this array corresponds to the total number of decoding steps and emphasizes that these candidates may not necessarily be limited to the top candidates.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.logprobsresult.chosencandidates.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
chosenCandidates: LogprobsCandidate[];
```

----------------------------------------

TITLE: Defining FunctionCall Property in FunctionCallPart Interface (TypeScript)
DESCRIPTION: This code snippet defines the functionCall property of the FunctionCallPart interface. The property is of type FunctionCall, indicating that it holds a function call object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncallpart.functioncall.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionCall: FunctionCall;
```

----------------------------------------

TITLE: Defining CountTokensRequest Interface
DESCRIPTION: This TypeScript interface is used to define the parameters for the countTokens method of the GenerativeModel. The interface includes optional properties for contents and a GenerateContentRequest, enforcing the rule that only one of them can be provided to prevent errors.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.counttokensrequest.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CountTokensRequest {
  contents?: Content[];
  generateContentRequest?: GenerateContentRequest;
}
```

----------------------------------------

TITLE: Defining ExecutableCode Interface in TypeScript
DESCRIPTION: TypeScript interface definition for executable code generated by the model. The interface specifies two properties: code (the executable code string) and language (the programming language of the code).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ExecutableCode 
```

----------------------------------------

TITLE: Defining FunctionResponse.name Property in TypeScript
DESCRIPTION: This code snippet defines the 'name' property of the FunctionResponse interface. It is a string type, representing the name of the function response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functionresponse.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
name: string;
```

----------------------------------------

TITLE: Defining the topP Property in GenerationConfig Interface in TypeScript
DESCRIPTION: The topP property is an optional number parameter in the GenerationConfig interface that controls nucleus sampling. It affects the randomness and diversity of generated content by considering only the tokens with top probability mass.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.topp.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
topP?: number;
```

----------------------------------------

TITLE: VideoMetadata Interface Definition
DESCRIPTION: Defines the VideoMetadata interface, which includes properties that describe the metadata of a video after it has been processed. Currently, it only contains the videoDuration property, which represents the duration of the video.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.videometadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface VideoMetadata 
```

----------------------------------------

TITLE: Defining GoogleSearchRetrievalTool Interface in TypeScript
DESCRIPTION: This code snippet defines the GoogleSearchRetrievalTool interface, which represents a retrieval tool powered by Google search. It contains an optional property 'googleSearchRetrieval' of type GoogleSearchRetrieval for configuring the search retrieval tool.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlesearchretrievaltool.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface GoogleSearchRetrievalTool {
    googleSearchRetrieval?: GoogleSearchRetrieval;
}
```

----------------------------------------

TITLE: Defining FileState Enum in TypeScript for Google Generative AI SDK
DESCRIPTION: Declaration of the FileState enum which tracks the processing state of File objects in the Google Generative AI JavaScript SDK. The enum defines four possible states: ACTIVE (when file processing is complete), FAILED (when processing encountered errors), PROCESSING (when file is being processed), and STATE_UNSPECIFIED (default or unknown state).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filestate.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum FileState 

```

----------------------------------------

TITLE: Defining FunctionDeclarationSchema Interface in TypeScript
DESCRIPTION: TypeScript interface definition for FunctionDeclarationSchema that specifies the structure of parameters passed to function declarations. It includes optional description and required fields, properties object, and type specification.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclarationschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionDeclarationSchema 
```

----------------------------------------

TITLE: Constructing GoogleGenerativeAIResponseError in TypeScript
DESCRIPTION: This constructor creates a new instance of the GoogleGenerativeAIResponseError class. It takes a required message parameter of type string and an optional response parameter of type T.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeairesponseerror._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(message: string, response?: T);
```

----------------------------------------

TITLE: Defining FunctionResponsePart.functionResponse Property in TypeScript
DESCRIPTION: Declaration of the functionResponse property in the FunctionResponsePart interface. The property is of type FunctionResponse and is used for handling function responses in the Generative AI library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functionresponsepart.functionresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionResponse: FunctionResponse;
```

----------------------------------------

TITLE: Defining EnhancedGenerateContentResponse.functionCalls Property Type Signature
DESCRIPTION: Type signature for the functionCalls property that returns an array of FunctionCall objects or undefined. The property is a method that throws an error if the prompt or candidate was blocked.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.enhancedgeneratecontentresponse.functioncalls.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionCalls: () => FunctionCall[] | undefined;
```

----------------------------------------

TITLE: Defining ObjectSchema Interface in TypeScript
DESCRIPTION: This snippet exports the ObjectSchema interface which extends BaseSchema, outlining the blueprint for JSON objects in the application. It includes properties for defining required keys and describes the structure of the object using schemas.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.objectschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ObjectSchema extends BaseSchema 

```

----------------------------------------

TITLE: Defining FunctionCall Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionCall interface, which represents a predicted function call returned from a generative AI model. It includes two properties: 'args' for the function arguments and 'name' for the function name.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functioncall.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionCall 
{
  args: object;
  name: string;
}
```

----------------------------------------

TITLE: Defining Code Execution Property in TypeScript
DESCRIPTION: This snippet defines the 'codeExecution' property as an empty object. It is intended to enable code execution features and may be extended in future developments.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.codeexecutiontool.codeexecution.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
codeExecution: {};  
```

----------------------------------------

TITLE: Defining Optional Tool Configuration in TypeScript
DESCRIPTION: Declares an optional toolConfig property of type ToolConfig in the StartChatParams interface, allowing flexible configuration for chat interactions
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.startchatparams.toolconfig.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
toolConfig?: ToolConfig;
```

----------------------------------------

TITLE: Defining videoMetadata Property in TypeScript
DESCRIPTION: This code snippet shows the TypeScript signature for the videoMetadata property of the FileMetadataResponse interface. It is an optional property of type VideoMetadata, which contains video metadata populated after processing is complete.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadataresponse.videometadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
videoMetadata?: VideoMetadata;
```

----------------------------------------

TITLE: Defining GoogleSearchRetrieval Interface in TypeScript
DESCRIPTION: This code snippet defines the GoogleSearchRetrieval interface, which represents a retrieval tool powered by Google search. It includes an optional property 'dynamicRetrievalConfig' of type DynamicRetrievalConfig.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlesearchretrieval.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface GoogleSearchRetrieval 

```

----------------------------------------

TITLE: Defining fileUri Property
DESCRIPTION: This snippet declares the fileUri property of the FileData interface in TypeScript. It specifies that fileUri is of type string, which is essential for representing the URI of a file. No additional dependencies are required for defining this property, but it should be utilized within the context of the FileData interface in the @google/generative-ai module.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filedata.fileuri.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
fileUri: string;
```

----------------------------------------

TITLE: Defining FunctionResponse Interface in TypeScript
DESCRIPTION: Interface definition for FunctionResponse that includes name and response properties. The interface captures the result output from a FunctionCall, containing the function name and a structured JSON response object that provides context back to the model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functionresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionResponse 
```

----------------------------------------

TITLE: Defining UploadFileResponse Interface in TypeScript
DESCRIPTION: The UploadFileResponse interface is defined to structure the response from the uploadFile method of the GoogleAIFileManager. It includes one property, 'file', which is of the type FileMetadataResponse. This interface is used to handle responses from the API call and provide metadata about the uploaded file.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.uploadfileresponse.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
export interface UploadFileResponse 
```

----------------------------------------

TITLE: Defining GoogleGenerativeAIResponseError.response Property in TypeScript
DESCRIPTION: This code snippet defines the 'response' property for the GoogleGenerativeAIResponseError class. The property is optional and has a generic type T.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeairesponseerror.response.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
response?: T;
```

----------------------------------------

TITLE: FileData Interface Definition
DESCRIPTION: Defines the structure of the FileData interface.  This interface contains information about an uploaded file, specifically its URI and MIME type. It's used to represent file data within the Generative AI API.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filedata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileData 
```

----------------------------------------

TITLE: Defining endIndex Property
DESCRIPTION: This snippet defines an optional property endIndex of type number within the CitationSource interface. It is used to indicate the ending index of a citation in the Generative AI framework.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.citationsource.endindex.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
endIndex?: number;
```

----------------------------------------

TITLE: Defining Array Schema Items Property in TypeScript
DESCRIPTION: Property definition that specifies the schema type for array entries in the ArraySchema class. The items property uses the Schema type to describe the structure of each element in the array.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.arrayschema.items.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
items: Schema;
```

----------------------------------------

TITLE: Defining CodeExecutionResult Output in TypeScript
DESCRIPTION: A string property that captures the output of code execution, including standard output for successful executions or error messages for failed executions
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.codeexecutionresult.output.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
output: string;
```

----------------------------------------

TITLE: Defining Code Execution Outcome Property in TypeScript
DESCRIPTION: This snippet defines the 'outcome' property as part of the CodeExecutionResult, indicating the result of a code execution process. It is essential for understanding what the result of executed code will be, specifically in the Generative AI realm. The property is typed as 'Outcome', which should be defined elsewhere in the codebase to capture various execution results.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.codeexecutionresult.outcome.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
outcome: Outcome;
```

----------------------------------------

TITLE: Defining cachedContent Property in TypeScript
DESCRIPTION: This code snippet shows the TypeScript definition of the `cachedContent` property within the `ModelParams` interface. The `cachedContent` property is optional, as indicated by the `?`, and its type is `CachedContent`. This allows the model to utilize or store cached content, likely for performance optimizations or consistent responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.modelparams.cachedcontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"cachedContent?: CachedContent;"
```

----------------------------------------

TITLE: EmbedContentRequest title property
DESCRIPTION: Defines the optional `title` property of the `EmbedContentRequest` interface. This property accepts a string value, presumably used to provide a descriptive title for the content being embedded. The title may be used for organization or retrieval purposes.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.embedcontentrequest.title.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"title?: string;"
```

----------------------------------------

TITLE: Defining ListCacheResponse Interface in TypeScript
DESCRIPTION: This code snippet defines the ListCacheResponse interface in TypeScript. It includes two properties: cachedContents (an array of CachedContent objects) and an optional nextPageToken (string).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.listcacheresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ListCacheResponse {
  cachedContents: CachedContent[];
  nextPageToken?: string;
}
```

----------------------------------------

TITLE: Defining GenerativeContentBlob Interface in TypeScript
DESCRIPTION: This code snippet defines the GenerativeContentBlob interface, which is used for sending image data. It includes two properties: 'data' for the base64-encoded image string, and 'mimeType' for the image format.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativecontentblob.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerativeContentBlob 
{
    data: string;
    mimeType: string;
}
```

----------------------------------------

TITLE: Defining TaskType Enum in TypeScript for Google Generative AI
DESCRIPTION: This TypeScript enum defines different task types for embedding content in the Google Generative AI library. It includes options for classification, clustering, document retrieval, query retrieval, semantic similarity, and an unspecified type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.tasktype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum TaskType 

```

----------------------------------------

TITLE: Defining Optional Block Reason Message in TypeScript
DESCRIPTION: This code snippet declares an optional property 'blockReasonMessage' of type string in TypeScript. The property is part of the PromptFeedback interface, used in a generative AI context to potentially hold messages explaining why a prompt was blocked.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.promptfeedback.blockreasonmessage.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
blockReasonMessage?: string;
```

----------------------------------------

TITLE: Declaring GoogleAICacheManager Class - TypeScript
DESCRIPTION: Class declaration for GoogleAICacheManager that provides functionality for managing Google AI content caches. The class includes methods for CRUD operations on content caches and requires an API key for initialization.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleAICacheManager 
```

----------------------------------------

TITLE: Defining SafetyRatings Array in TypeScript
DESCRIPTION: Declares a property of type SafetyRating array on the PromptFeedback class, allowing access to safety ratings for a generated prompt
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.promptfeedback.safetyratings.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
safetyRatings: SafetyRating[];
```

----------------------------------------

TITLE: Defining EnumStringSchema Interface in TypeScript
DESCRIPTION: This code snippet defines the EnumStringSchema interface, which extends BaseSchema. It specifies the structure for describing a string enum, including its possible values, format, and type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.enumstringschema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface EnumStringSchema extends BaseSchema 
{
    enum: string[];
    format: "enum";
    type: typeof SchemaType.STRING;
}
```

----------------------------------------

TITLE: Defining ExecutableCode.code Property in TypeScript
DESCRIPTION: This snippet shows the TypeScript signature for the 'code' property of the ExecutableCode interface. It represents the actual code string to be executed.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecode.code.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
code: string;
```

----------------------------------------

TITLE: Defining Prompt Token Count in TypeScript
DESCRIPTION: Declares a numeric property to track the number of tokens used in a generative AI prompt. This property helps measure input complexity and resource usage.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.usagemetadata.prompttokencount.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
promptTokenCount: number;
```

----------------------------------------

TITLE: Defining Optional Tools Array in TypeScript
DESCRIPTION: This snippet defines the 'tools' property as an optional array of Tool objects in the CachedContentBase class. It is used to specify a set of tools that can be associated with cached content. The 'tools' property is not mandatory, meaning that an instance of CachedContentBase may or may not include it.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.cachedcontentbase.tools.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
tools?: Tool[];

```

----------------------------------------

TITLE: Defining Optional Contents Property
DESCRIPTION: This snippet defines an optional property 'contents' in the 'CountTokensRequest' interface, which can hold an array of 'Content' type elements. The usage of the '?' character indicates that this property may be undefined.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.counttokensrequest.contents.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
contents?: Content[];
```

----------------------------------------

TITLE: Defining Optional GroundingSupports Property in TypeScript
DESCRIPTION: This snippet defines an optional property `groundingSupports` within the `GroundingMetadata` module. It is an array of `GroundingSupport` objects, which implies it can hold multiple entities that provide grounding support, if any. The property is optional, denoted by the `?`, meaning its presence is not mandatory.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingmetadata.groundingsupports.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
groundingSupports?: GroundingSupport[];
```

----------------------------------------

TITLE: Defining GenerativeContentBlob Interface in TypeScript
DESCRIPTION: This code snippet defines the GenerativeContentBlob interface, which is used for sending an image. It includes two properties: data for the base64-encoded image string, and mimeType for specifying the image format.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.generativecontentblob.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerativeContentBlob {
    data: string;
    mimeType: string;
}
```

----------------------------------------

TITLE: Defining ModelParams Tools Property in TypeScript
DESCRIPTION: The snippet documents the tools property of the ModelParams interface in TypeScript. This property is optional and is expected to be an array of Tool objects, where each Tool represents a specific functionality. This setup assumes a dependency on the Tool type being defined elsewhere in the project.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.modelparams.tools.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
tools?: Tool[];
```

----------------------------------------

TITLE: Defining LogprobsCandidate Interface TypeScript
DESCRIPTION: Defines the interface LogprobsCandidate for use in a generative AI setting. This interface includes properties for log probability, token string value, and token ID, which are essential for determining candidate details in probabilistic models. All properties are primitive types with `number` and `string`. No external dependencies are required.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.logprobscandidate.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface LogprobsCandidate
```

----------------------------------------

TITLE: Defining fileData Property in ExecutableCodePart Interface (TypeScript)
DESCRIPTION: This code snippet shows the TypeScript signature for the fileData property in the ExecutableCodePart interface. The property is optional and has a type of 'never', indicating it should never be used or assigned a value.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecodepart.filedata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
fileData?: never;
```

----------------------------------------

TITLE: Initializing GoogleAICacheManager in TypeScript
DESCRIPTION: Constructor signature for creating a new instance of the GoogleAICacheManager class. It requires an API key string parameter and accepts an optional RequestOptions parameter.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager._constructor_.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
constructor(apiKey: string, _requestOptions?: RequestOptions);
```

----------------------------------------

TITLE: Declaring cachedContentTokenCount Property in TypeScript
DESCRIPTION: Defines an optional number property that represents the total token count in the cached portion of a prompt within the UsageMetadata interface.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.usagemetadata.cachedcontenttokencount.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
cachedContentTokenCount?: number;
```

----------------------------------------

TITLE: Defining SafetyRating.probability Property in TypeScript
DESCRIPTION: This code snippet defines the probability property for the SafetyRating class. The property is of type HarmProbability, which likely represents a measure of potential harm or safety risk.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.safetyrating.probability.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
probability: HarmProbability;
```

----------------------------------------

TITLE: Defining ExecutableCodePart Interface in TypeScript
DESCRIPTION: This code snippet defines the ExecutableCodePart interface, which represents content parts containing executable code generated by a model. It includes properties for executable code and optional properties for various related data.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.executablecodepart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ExecutableCodePart 
{
  codeExecutionResult?: never;
  executableCode: ExecutableCode;
  fileData?: never;
  functionCall?: never;
  functionResponse?: never;
  inlineData?: never;
  text?: never;
}
```

----------------------------------------

TITLE: Defining candidatesTokenCount Property in TypeScript
DESCRIPTION: This snippet shows the TypeScript signature for the candidatesTokenCount property of the UsageMetadata interface. It represents the total number of tokens across the generated candidates and is of type number.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.usagemetadata.candidatestokencount.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
candidatesTokenCount: number;
```

----------------------------------------

TITLE: Defining Role Property in TypeScript
DESCRIPTION: This snippet defines a property 'role' as a string type, which is part of the content structure used in the Generative AI framework. It requires TypeScript as a dependency for proper type checking and structure. The expected input is a string value that represents the role, while the output is the definition of the role within the content framework.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.content.role.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
role: string;
```

----------------------------------------

TITLE: Defining Optional System Instruction Property
DESCRIPTION: This snippet declares the 'systemInstruction' property, which can optionally be a string, a 'Part', or 'Content'. This property is part of the 'CachedContentBase' interface, and it is designed to hold various content types depending on the use case. The property helps in managing different forms of data that can be cached for generative AI applications.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.cachedcontentbase.systeminstruction.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
systemInstruction?: string | Part | Content;
```

----------------------------------------

TITLE: Defining Optional Property groundingChunks in TypeScript
DESCRIPTION: This snippet defines the optional property groundingChunks for the GroundingMetadata interface, allowing the property to hold an array of GroundingChunk objects. The use of the '?' indicates that this property is optional, and it may not be present in every instance of GroundingMetadata.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingmetadata.groundingchunks.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
groundingChunks?: GroundingChunk[];
```

----------------------------------------

TITLE: Defining GenerativeContentBlob Data Property in TypeScript
DESCRIPTION: This code snippet defines the 'data' property for the GenerativeContentBlob class. It specifies that the property is of type string and is intended to store image data as a base64-encoded string.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativecontentblob.data.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
data: string;
```

----------------------------------------

TITLE: Defining FileState enum in TypeScript for @google/generative-ai
DESCRIPTION: Declaration of the FileState enum which represents different processing states of a File object. The states include ACTIVE (successfully processed), FAILED (processing failed), PROCESSING (currently being processed), and STATE_UNSPECIFIED (default/unknown state).
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filestate.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum FileState 

```

----------------------------------------

TITLE: TypeScript Interface Property Definition for FunctionCallingConfig.allowedFunctionNames
DESCRIPTION: Defines the optional allowedFunctionNames property that accepts an array of strings representing the function names that are allowed to be called in the function calling configuration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncallingconfig.allowedfunctionnames.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
allowedFunctionNames?: string[];
```

----------------------------------------

TITLE: Uploading Content to Cache using GoogleAICacheManager in TypeScript
DESCRIPTION: Method signature for the create() function in the GoogleAICacheManager class that allows uploading a new content cache. It accepts createOptions of type CachedContentCreateParams and returns a Promise that resolves to a CachedContent object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager.create.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
create(createOptions: CachedContentCreateParams): Promise<CachedContent>;
```

----------------------------------------

TITLE: Defining metadata property in TypeScript for ErrorDetails interface
DESCRIPTION: This code snippet defines an optional property 'metadata' in the ErrorDetails interface. The property is a record that can store any key-value pairs with unknown types. It is flexible to accommodate various data structures as needed for error details.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.errordetails.metadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
metadata?: Record<string, unknown>;
```

----------------------------------------

TITLE: Defining BlockReason Enum in TypeScript
DESCRIPTION: Enumerates the possible reasons why a prompt may be blocked in the generative AI system. Contains three possible values: BLOCKED_REASON_UNSPECIFIED, OTHER, and SAFETY.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.blockreason.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum BlockReason 
```

----------------------------------------

TITLE: Defining FunctionResponse Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionResponse interface, which has two properties: 'name' of type string and 'response' of type object. It represents the result output from a FunctionCall, containing the function name and a structured JSON object with the function's output.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functionresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionResponse 
{
  name: string;
  response: object;
}
```

----------------------------------------

TITLE: Defining 'name' Property in CachedContent Interface (TypeScript)
DESCRIPTION: This code snippet shows the TypeScript signature for the optional 'name' property of the CachedContent interface. It is defined as an optional string type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.cachedcontent.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
name?: string;
```

----------------------------------------

TITLE: Defining groundingMetadata Property in TypeScript
DESCRIPTION: Declares the groundingMetadata property of the GenerateContentCandidate class. It is an optional property of type GroundingMetadata, which likely contains metadata related to search grounding for the generated content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentcandidate.groundingmetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
groundingMetadata?: GroundingMetadata;
```

----------------------------------------

TITLE: Defining searchEntryPoint Property in TypeScript
DESCRIPTION: This snippet defines the searchEntryPoint property of the GroundingMetadata interface, which allows for specifying a Google search entry point for follow-up web searches. It ensures that this property can be optionally included in the metadata structure.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingmetadata.searchentrypoint.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
searchEntryPoint?: SearchEntryPoint;
```

----------------------------------------

TITLE: Defining CodeExecutionResult.output Property in TypeScript
DESCRIPTION: Defines the 'output' property of the CodeExecutionResult class. This property contains the stdout when code execution is successful, or stderr or other description otherwise.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.codeexecutionresult.output.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
output: string;
```

----------------------------------------

TITLE: GroundingSupportSegment.startIndex Property Declaration
DESCRIPTION: This code snippet shows the declaration of the `startIndex` property within the `GroundingSupportSegment` class. It is an optional number representing the start index in bytes from the beginning of the Part.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingsupportsegment.startindex.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"startIndex?: number;"
```

----------------------------------------

TITLE: Defining FileMetadataResponse Interface in TypeScript
DESCRIPTION: TypeScript interface declaration for FileMetadataResponse which encapsulates file metadata returned from the server. The interface defines various properties related to file information and status.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadataresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FileMetadataResponse 
```

----------------------------------------

TITLE: Defining totalTokenCount Property in TypeScript Interface
DESCRIPTION: TypeScript interface property definition for tracking the total number of tokens used in a generation request, including both the prompt and response candidates.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.usagemetadata.totaltokencount.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
totalTokenCount: number;
```

----------------------------------------

TITLE: Defining FunctionCallingMode Enum in TypeScript
DESCRIPTION: This code snippet defines the FunctionCallingMode enum, which specifies different modes for function calling in the Google Generative AI library. It includes options like ANY, AUTO, MODE_UNSPECIFIED, and NONE.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncallingmode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare enum FunctionCallingMode 
```

----------------------------------------

TITLE: GoogleAIFileManager Class Declaration in TypeScript
DESCRIPTION: Class declaration for the GoogleAIFileManager which provides functionality for managing Google AI file uploads. This includes methods for uploading, retrieving, listing, and deleting files.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleAIFileManager 
```

----------------------------------------

TITLE: Defining Optional Property in TypeScript Interface
DESCRIPTION: This code snippet declares an optional property generateContentRequest within the CountTokensRequest interface. This property is of the type GenerateContentRequest, which should be defined elsewhere in the codebase. It leverages TypeScript's optional chaining to indicate that this property is not mandatory.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.counttokensrequest.generatecontentrequest.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
generateContentRequest?: GenerateContentRequest;
```

----------------------------------------

TITLE: Defining citationSources in TypeScript Interface
DESCRIPTION: Defines the citationSources property as an array of CitationSource objects. This property is part of the CitationMetadata interface, used to store a list of citation sources in generative AI contexts. The CitationSource type must be defined elsewhere in the application. There are no direct input or output functions associated with this property; it's purely a data structure definition.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.citationmetadata.citationsources.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
citationSources: CitationSource[];
```

----------------------------------------

TITLE: Defining ChatSession.model Property in TypeScript
DESCRIPTION: TypeScript signature for the model property of the ChatSession class, which is defined as a string type that likely references the specific generative model being used in the chat session.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.chatsession.model.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
model: string;
```

----------------------------------------

TITLE: Defining systemInstruction Property in TypeScript
DESCRIPTION: This code snippet shows the TypeScript signature for the systemInstruction property of the CachedContentBase class. It is an optional property that can be a string, Part, or Content type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentbase.systeminstruction.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
systemInstruction?: string | Part | Content;
```

----------------------------------------

TITLE: Defining frequencyPenalty Property in GenerationConfig Interface (TypeScript)
DESCRIPTION: Declares the frequencyPenalty property as an optional number in the GenerationConfig interface. This property is used to apply a penalty to the probability of generating tokens that have already appeared in the response, based on their frequency.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.frequencypenalty.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
frequencyPenalty?: number;
```

----------------------------------------

TITLE: Defining Function Declaration Properties Schema in TypeScript
DESCRIPTION: Defines a properties object that maps string keys to FunctionDeclarationSchemaProperty values. This schema is used to specify the format and structure of function parameters in the Google Generative AI JavaScript library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclarationschema.properties.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
properties: {
        [k: string]: FunctionDeclarationSchemaProperty;
    };
```

----------------------------------------

TITLE: Defining maxItems Property in ArraySchema Class (TypeScript)
DESCRIPTION: This code snippet defines the maxItems property for the ArraySchema class. It is an optional number property that represents the maximum number of items allowed in the array.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.arrayschema.maxitems.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
maxItems?: number;
```

----------------------------------------

TITLE: GroundingSupportSegment.text Property Definition
DESCRIPTION: This code snippet shows the definition of the `text` property within the `GroundingSupportSegment` class. The `text` property is an optional string, meaning it can either contain a string value or be undefined. It represents the text associated with a specific segment of the response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingsupportsegment.text.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
text?: string;
```
```

----------------------------------------

TITLE: Defining the 'category' Property Type in SafetyRating Class (TypeScript)
DESCRIPTION: This code defines the 'category' property of the SafetyRating class in the @google/generative-ai package. The property is typed as HarmCategory, which represents different categories of potentially harmful content that can be identified by the model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.safetyrating.category.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
category: HarmCategory;
```

----------------------------------------

TITLE: Deleting a file using GoogleAIFileManager (TypeScript)
DESCRIPTION: This snippet shows the signature of the `deleteFile` method within the `GoogleAIFileManager` class. It accepts a `fileId` as a string and returns a Promise that resolves to void, indicating that the file deletion operation is asynchronous and doesn't return a value upon completion.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager.deletefile.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
deleteFile(fileId: string): Promise<void>;
```
```

----------------------------------------

TITLE: CitationSource license property definition
DESCRIPTION: This code snippet defines the `license` property within the `CitationSource` class. The property is optional (indicated by the `?` symbol) and is of type `string`. It likely represents the license information associated with a citation source.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.citationsource.license.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"license?: string;"
```

----------------------------------------

TITLE: Defining Start Index Property
DESCRIPTION: This snippet defines an optional property 'startIndex' in the CitationSource interface, indicating the starting index value which is expected to be a number. This property is utilized for pagination or indexing purposes within the context of generative AI citations.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.citationsource.startindex.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
startIndex?: number;
```

----------------------------------------

TITLE: Defining Tool Config Interface
DESCRIPTION: This interface defines the configuration for a tool. It includes a `functionCallingConfig` property of type `FunctionCallingConfig`.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_19

LANGUAGE: typescript
CODE:
```
export interface ToolConfig {
    // (undocumented)
    functionCallingConfig: FunctionCallingConfig;
}
```

----------------------------------------

TITLE: Defining FileMetadata.mimeType property
DESCRIPTION: This code snippet shows the definition of the `mimeType` property within the `FileMetadata` class. The property is of type string and represents the MIME type of a file.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadata.mimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
mimeType: string;
```
```

----------------------------------------

TITLE: Defining Dynamic Retrieval Threshold Property in TypeScript
DESCRIPTION: This TypeScript code snippet defines a property `dynamicThreshold` within the `DynamicRetrievalConfig` interface or class. The property is optional and is of the type `number`. If not specified, a system-defined default value will be applied. It is used for setting thresholds in dynamic retrieval operations, which are part of generative AI configurations.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.dynamicretrievalconfig.dynamicthreshold.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
dynamicThreshold?: number;
```

----------------------------------------

TITLE: Defining 'tools' Property in CachedContentBase Class (TypeScript)
DESCRIPTION: This code snippet defines the 'tools' property for the CachedContentBase class. It is an optional property that accepts an array of Tool objects.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentbase.tools.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
tools?: Tool[];
```

----------------------------------------

TITLE: ArraySchema.minItems Property Declaration
DESCRIPTION: This code snippet shows the declaration of the `minItems` property within the `ArraySchema` class.  It is an optional numeric property that indicates the minimum number of elements expected in the array it describes.  If absent, there is no minimum limit.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.arrayschema.minitems.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"minItems?: number;"
```

----------------------------------------

TITLE: Defining EmbedContentResponse.embedding Property Type in TypeScript
DESCRIPTION: Type definition for the embedding property of the EmbedContentResponse class. The property returns a ContentEmbedding object that contains the embedded representation of content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.embedcontentresponse.embedding.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
embedding: ContentEmbedding;
```

----------------------------------------

TITLE: CitationMetadata Interface Definition
DESCRIPTION: Defines the `CitationMetadata` interface in TypeScript. This interface is used to represent citation information associated with generated content. It contains a single property, `citationSources`, which is an array of `CitationSource` objects.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.citationmetadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CitationMetadata 
```

----------------------------------------

TITLE: TopCandidates Interface Declaration
DESCRIPTION: This code snippet defines the `TopCandidates` interface in TypeScript.  It's used to represent a set of candidate results from a generative AI model, specifically those with the highest log probabilities. The interface contains a single property, `candidates`, which is an array of `LogprobsCandidate` objects.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.topcandidates.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface TopCandidates 
```

----------------------------------------

TITLE: Defining CodeExecutionResult.outcome Property in TypeScript
DESCRIPTION: This code snippet defines the 'outcome' property for the CodeExecutionResult class. The property is of type Outcome, which likely represents the possible results of a code execution.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.codeexecutionresult.outcome.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
outcome: Outcome;
```

----------------------------------------

TITLE: Defining ListFilesResponse Interface in TypeScript
DESCRIPTION: This snippet defines the ListFilesResponse interface, which contains an array of FileMetadataResponse objects and an optional nextPageToken string. It represents the structure of the response returned when listing files using the GoogleAIFileManager.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.listfilesresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ListFilesResponse 
{
  files: FileMetadataResponse[];
  nextPageToken?: string;
}
```

----------------------------------------

TITLE: Declaring TTL Property in TypeScript
DESCRIPTION: Defines an optional string property 'ttl' that accepts a protobuf Duration format value (e.g. '3.0001s') to specify cache duration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontent.ttl.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
ttl?: string;
```

----------------------------------------

TITLE: Declaring URI Property in GroundingChunkWeb - TypeScript
DESCRIPTION: Declares an optional URI property as part of the GroundingChunkWeb class, intended to hold a string reference to a URI. This snippet illustrates the structure of the URI property within the GroundingChunkWeb component. No additional dependencies are required as it is a part of the TypeScript code base. The property does not enforce an input value (optional) and has no specific constraints except the type requirement of being a string.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingchunkweb.uri.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
uri?: string;
```

----------------------------------------

TITLE: Defining FunctionResponsePart Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionResponsePart interface, which includes various optional properties and a required functionResponse property of type FunctionResponse.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functionresponsepart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionResponsePart 
{
  codeExecutionResult?: never;
  executableCode?: never;
  fileData?: never;
  functionCall?: never;
  functionResponse: FunctionResponse;
  inlineData?: never;
  text?: never;
}
```

----------------------------------------

TITLE: Defining displayName Property in FileMetadataResponse Interface in TypeScript
DESCRIPTION: Defines an optional displayName property of type string within the FileMetadataResponse interface from the @google/generative-ai package.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadataresponse.displayname.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
displayName?: string;
```

----------------------------------------

TITLE: Defining BooleanSchema Type Property in TypeScript
DESCRIPTION: Type definition for the type property of BooleanSchema class that explicitly sets it to SchemaType.BOOLEAN. This property is used to identify the schema as a boolean type schema.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.booleanschema.type.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
type: typeof SchemaType.BOOLEAN;
```

----------------------------------------

TITLE: CachedContent ttl property
DESCRIPTION: Defines the `ttl` property within the `CachedContent` class. This property represents the duration for which the content should be cached, expressed as a string in protobuf.Duration format.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.cachedcontent.ttl.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"ttl?: string;"
```

----------------------------------------

TITLE: Defining ArraySchema Type Property in TypeScript
DESCRIPTION: Defines the 'type' property for the ArraySchema class which is set to the ARRAY constant from the SchemaType enum. This property specifies that the schema is of array type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.arrayschema.type.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
type: typeof SchemaType.ARRAY;
```

----------------------------------------

TITLE: Defining nextPageToken Property in TypeScript
DESCRIPTION: TypeScript type definition for the optional nextPageToken property in the ListCacheResponse interface. This property is used for pagination purposes when listing cached responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.listcacheresponse.nextpagetoken.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
nextPageToken?: string;
```

----------------------------------------

TITLE: Defining FunctionCall Interface in TypeScript
DESCRIPTION: TypeScript interface definition for FunctionCall that specifies the structure of predicted function calls. It contains a name string property and an args object property for parameters and their values.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncall.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionCall 
```

----------------------------------------

TITLE: Defining ExecutableCode Interface
DESCRIPTION: This snippet defines the ExecutableCode interface, which represents code generated by the model to be executed, with properties specifying the code and its language. It is utilized in the context of automatically executing code and receiving results. The primary dependencies are related to the types defined within the package, particularly ExecutableCodeLanguage.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.executablecode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ExecutableCode \n
```

----------------------------------------

TITLE: ListFilesResponse nextPageToken property
DESCRIPTION: Defines the `nextPageToken` property as an optional string within the `ListFilesResponse` interface. This token is used for pagination, allowing retrieval of subsequent pages of file listings. If present, it indicates that more files are available.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.listfilesresponse.nextpagetoken.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
nextPageToken?: string;
```
```

----------------------------------------

TITLE: ArraySchema Items Property Definition
DESCRIPTION: Defines the `items` property within the `ArraySchema` class.  This property is of type `Schema`, indicating that it holds the schema definition for the array's elements. It allows specification of the expected structure and data types of elements contained within the array.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.arrayschema.items.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"items: Schema;"
```

----------------------------------------

TITLE: Declaring mimeType Property in GenerativeContentBlob Class in TypeScript
DESCRIPTION: Type definition for the mimeType property of the GenerativeContentBlob class. The property is declared as a string type and is used to specify the MIME type of the blob content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativecontentblob.mimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mimeType: string;
```

----------------------------------------

TITLE: Defining GenerateContentCandidate Interface in TypeScript
DESCRIPTION: TypeScript interface definition for GenerateContentCandidate that specifies the structure of content generation responses. Contains properties for content, metadata, safety ratings, and various probability scores.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentcandidate.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface GenerateContentCandidate 
```

----------------------------------------

TITLE: Defining Cached Content Property
DESCRIPTION: This snippet defines the 'cachedContent' property within the 'CachedContentUpdateParams' interface, which is a crucial part of managing content updates in the generative AI framework. The property is typed as 'CachedContentUpdateInputFields', representing the structure of the content that can be cached. It is essential for ensuring type safety and clarity in the use of cached content within the API.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentupdateparams.cachedcontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
cachedContent: CachedContentUpdateInputFields;
```

----------------------------------------

TITLE: Specifying Object Type in TypeScript
DESCRIPTION: The `ObjectSchema.type` property is defined as a type of `SchemaType.OBJECT`. This signifies that the type property is expected to be an OBJECT schema type as defined in the SchemaType enum. No additional setup is required as it directly makes use of the existing SchemaType object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.objectschema.type.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
type: typeof SchemaType.OBJECT;
```

----------------------------------------

TITLE: Defining finishReason Property in TypeScript
DESCRIPTION: This snippet defines the finishReason property as an optional member of the GenerateContentCandidate class. It indicates the reason a content generation operation finished, if applicable. The property is typed as FinishReason. The implementation suggests that it is part of a broader API related to generative AI capabilities.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentcandidate.finishreason.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
finishReason?: FinishReason;
```

----------------------------------------

TITLE: Defining mimeType Property in GenerativeContentBlob Class (TypeScript)
DESCRIPTION: This code snippet defines the mimeType property for the GenerativeContentBlob class. The property is of type string and represents the MIME type of the content blob.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.generativecontentblob.mimetype.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
mimeType: string;
```

----------------------------------------

TITLE: Defining RpcStatus Interface in TypeScript
DESCRIPTION: TypeScript interface definition for standard RPC error status object. Contains properties for error code, error message, and optional array of error details.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.rpcstatus.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface RpcStatus 
```

----------------------------------------

TITLE: ExecutableCode.code Property Definition
DESCRIPTION: This code snippet defines the `code` property within the `ExecutableCode` class. The `code` property is a string that represents the code to be executed. It is a core part of the ExecutableCode interface for specifying the actual code.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.executablecode.code.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"code: string;"
```

----------------------------------------

TITLE: Outcome Enum for Operation Results
DESCRIPTION: Enum defining possible outcomes of AI operations, including success, failure, and timeout scenarios
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai-server.api.md#2025-04-21_snippet_11

LANGUAGE: typescript
CODE:
```
export enum Outcome {
    OUTCOME_DEADLINE_EXCEEDED = "outcome_deadline_exceeded",
    OUTCOME_FAILED = "outcome_failed",
    OUTCOME_OK = "outcome_ok",
    OUTCOME_UNSPECIFIED = "outcome_unspecified"
}
```

----------------------------------------

TITLE: Defining FunctionCall Property in FunctionCallPart Interface in TypeScript
DESCRIPTION: Property signature for the functionCall property of the FunctionCallPart interface. This property has a type of FunctionCall which is likely used for storing function call information in generative AI responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functioncallpart.functioncall.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionCall: FunctionCall;
```

----------------------------------------

TITLE: Defining createTime Property in FileMetadataResponse Interface (TypeScript)
DESCRIPTION: TypeScript signature for the createTime property which is part of the FileMetadataResponse interface. This property stores the creation timestamp of a file as a string value.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadataresponse.createtime.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
createTime: string;
```

----------------------------------------

TITLE: Defining Single Request Options Interface
DESCRIPTION: This interface extends the `RequestOptions` interface and adds an optional `signal` property of type `AbortSignal`.  The signal allows for cancellation of the request.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_13

LANGUAGE: typescript
CODE:
```
export interface SingleRequestOptions extends RequestOptions {
    signal?: AbortSignal;
}
```

----------------------------------------

TITLE: VideoMetadata videoDuration Property Declaration
DESCRIPTION: This code snippet shows the declaration of the `videoDuration` property within the `VideoMetadata` class. It's a string that follows the Google Protobuf Duration format. It represents how long the video is.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.videometadata.videoduration.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"videoDuration: string;"
```

----------------------------------------

TITLE: Defining Schema Type in TypeScript for Generative AI Library
DESCRIPTION: This code snippet defines the Schema type as a union of various schema types. It represents a subset of OpenAPI 3.0 schema object used for defining input/output data formats in the @google/generative-ai library.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.schema.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type Schema = StringSchema | NumberSchema | IntegerSchema | BooleanSchema | ArraySchema | ObjectSchema;
```

----------------------------------------

TITLE: Defining CachedContentUpdateParams Interface in TypeScript
DESCRIPTION: Interface definition for CachedContentUpdateParams that specifies the structure of parameters used when updating cached content. Contains two properties: cachedContent of type CachedContentUpdateInputFields and an optional updateMask array of strings for protobuf field masking.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentupdateparams.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CachedContentUpdateParams 
```

----------------------------------------

TITLE: Defining maxItems Property in ArraySchema Class (TypeScript)
DESCRIPTION: This code snippet defines the maxItems property for the ArraySchema class. It is an optional number property that specifies the maximum number of items allowed in the array.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.arrayschema.maxitems.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
maxItems?: number;
```

----------------------------------------

TITLE: Defining cachedContent Property in GenerateContentRequest Class
DESCRIPTION: Type definition for the optional cachedContent property that accepts a string identifier referencing a cached content object. This property stores the name of a CachedContent rather than the actual cache object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentrequest.cachedcontent.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
cachedContent?: string;
```

----------------------------------------

TITLE: Declaring avgLogprobs Property in TypeScript
DESCRIPTION: This code snippet defines the avgLogprobs property for the GenerateContentCandidate class. It is an optional number property that represents the average log probability score of the candidate.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentcandidate.avglogprobs.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
avgLogprobs?: number;
```

----------------------------------------

TITLE: Defining the message property in RpcStatus interface in TypeScript
DESCRIPTION: TypeScript definition for the 'message' property of the RpcStatus interface, which stores a developer-facing error message. This property is part of RPC status information typically used in error handling.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.rpcstatus.message.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
message: string;
```

----------------------------------------

TITLE: Defining ListFilesResponse Interface in TypeScript
DESCRIPTION: This TypeScript interface defines the structure of the response from the listFiles() method of GoogleAIFileManager. It includes an array of FileMetadataResponse objects and an optional nextPageToken string for pagination.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.listfilesresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface ListFilesResponse 
{
  files: FileMetadataResponse[];
  nextPageToken?: string;
}
```

----------------------------------------

TITLE: Defining FunctionResponsePart Interface in TypeScript
DESCRIPTION: This code snippet defines the FunctionResponsePart interface, which represents content parts for function responses. It includes properties for function response, optional code execution results, executable code, file data, function calls, inline data, and text.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functionresponsepart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface FunctionResponsePart 
{
  codeExecutionResult?: never;
  executableCode?: never;
  fileData?: never;
  functionCall?: never;
  functionResponse: FunctionResponse;
  inlineData?: never;
  text?: never;
}
```

----------------------------------------

TITLE: Defining VideoMetadata Property in FileMetadataResponse Interface (TypeScript)
DESCRIPTION: This code snippet defines the videoMetadata property in the FileMetadataResponse interface. It is an optional property of type VideoMetadata, which contains video metadata information after processing is complete.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.filemetadataresponse.videometadata.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
videoMetadata?: VideoMetadata;
```

----------------------------------------

TITLE: Defining NumberSchema.format Property in TypeScript
DESCRIPTION: This code snippet defines the 'format' property for the NumberSchema class. It is an optional property that specifies the format of a number, which can be either 'float' or 'double'.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.numberschema.format.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
format?: "float" | "double";
```

----------------------------------------

TITLE: Defining GenerativeModel.tools Property in TypeScript
DESCRIPTION: This code snippet defines the 'tools' property for the GenerativeModel class. It is an optional array of Tool objects, allowing for flexibility in model configuration.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.tools.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
tools?: Tool[];
```

----------------------------------------

TITLE: Defining CountTokensResponse Interface TypeScript
DESCRIPTION: This TypeScript snippet defines the CountTokensResponse interface, which is used as a response when invoking the countTokens method from GenerativeModel. It includes a property totalTokens, which is of number type and presumably represents the total number of tokens counted. There are no specified dependencies beyond the TypeScript language.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.counttokensresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CountTokensResponse 
```

----------------------------------------

TITLE: Defining the UploadFileResponse interface in TypeScript
DESCRIPTION: This code snippet defines the `UploadFileResponse` interface in TypeScript.  It specifies that the response contains a `file` property, which is of type `FileMetadataResponse`. This interface is the expected return type from the `GoogleAIFileManager.uploadFile()` method.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.uploadfileresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface UploadFileResponse 
```

----------------------------------------

TITLE: Defining EnumStringSchema Type Property in Google Generative AI - TypeScript
DESCRIPTION: Defines the type property of EnumStringSchema in TypeScript, associated with the SchemaType.STRING constant. This property is part of the Google Generative AI library's structure for representing schemas. It requires the inclusion of the EnumStringSchema module and proper installation of the Google Generative AI package.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.enumstringschema.type.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
type: typeof SchemaType.STRING;
```

----------------------------------------

TITLE: Defining status Property in GoogleGenerativeAIFetchError Class (TypeScript)
DESCRIPTION: This code snippet defines the status property for the GoogleGenerativeAIFetchError class. The property is of type number and is optional, as indicated by the question mark.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeaifetcherror.status.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
status?: number;
```

----------------------------------------

TITLE: Defining Model Property Type in GenerativeModel
DESCRIPTION: TypeScript type definition for the model property in the GenerativeModel class. The property is defined as a string type that represents the model identifier.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.model.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
model: string;
```

----------------------------------------

TITLE: Defining statusText Property in GoogleGenerativeAIFetchError Class (TypeScript)
DESCRIPTION: This code snippet defines the statusText property for the GoogleGenerativeAIFetchError class. It is an optional string property that likely represents the status text of an HTTP response when a fetch error occurs.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeaifetcherror.statustext.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
statusText?: string;
```

----------------------------------------

TITLE: Defining Model Property in TypeScript
DESCRIPTION: This snippet defines the 'model' property as a string within the ModelParams interface. It is essential for specifying the model type when using the Generative AI library. The defined structure ensures type safety and clarity in API usage.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.modelparams.model.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
model: string;
```

----------------------------------------

TITLE: Updating Cache Content with GoogleAICacheManager in TypeScript
DESCRIPTION: Method signature for updating existing cached content through the GoogleAICacheManager. Takes a name identifier and update parameters, returns a Promise resolving to the updated CachedContent object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager.update.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
update(name: string, updateParams: CachedContentUpdateParams): Promise<CachedContent>;
```

----------------------------------------

TITLE: Defining FunctionResponsePart.functionResponse Property in TypeScript
DESCRIPTION: TypeScript signature for the functionResponse property of the FunctionResponsePart interface, indicating it has a type of FunctionResponse.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functionresponsepart.functionresponse.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
functionResponse: FunctionResponse;
```

----------------------------------------

TITLE: GroundingChunk Interface Declaration
DESCRIPTION: Defines the `GroundingChunk` interface in TypeScript. It is used to represent a chunk of grounding data, potentially obtained from the web. The interface currently has one optional property `web` of type `GroundingChunkWeb`.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingchunk.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare interface GroundingChunk 
```

----------------------------------------

TITLE: Defining Timeout Property for RequestOptions in TypeScript
DESCRIPTION: This snippet defines an optional timeout property of type number for the RequestOptions interface. This allows setting a limit on the duration of requests made to the API. The property is defined as optional (using the '?' operator), meaning it may or may not be included when creating a RequestOptions object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.requestoptions.timeout.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
timeout?: number;
```

----------------------------------------

TITLE: Defining Base URL Property in TypeScript
DESCRIPTION: This snippet defines an optional property 'baseUrl' of type string for request options in the Generative AI API. If not specified, it defaults to 'https://generativelanguage.googleapis.com'. This property is crucial for ensuring API requests are directed to the correct endpoint.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.requestoptions.baseurl.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
baseUrl?: string;
```

----------------------------------------

TITLE: Defining the HarmBlockThreshold Enum in Typescript
DESCRIPTION: Defines the `HarmBlockThreshold` enum, which specifies different levels of harm blocking. These thresholds can be used to configure the safety settings of the Generative AI model.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_6

LANGUAGE: typescript
CODE:
```
//@public
export enum HarmBlockThreshold {
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE",
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE",
    BLOCK_NONE = "BLOCK_NONE",
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH",
    HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Listing Content Caches in Google AI TypeScript SDK
DESCRIPTION: Method signature for listing all uploaded content caches in the Google AI service. Accepts optional ListParams for filtering and returns a Promise containing ListCacheResponse.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager.list.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
list(listParams?: ListParams): Promise<ListCacheResponse>;
```

----------------------------------------

TITLE: Defining SimpleStringSchema.format Property in TypeScript
DESCRIPTION: This code snippet defines the type of the 'format' property for the SimpleStringSchema class. It is an optional property that can either be the string 'date-time' or undefined.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.simplestringschema.format.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
format?: "date-time" | undefined;
```

----------------------------------------

TITLE: Defining CachedContentUpdateInputFields TypeScript Interface
DESCRIPTION: Defines an interface with optional properties for updating cache expiration parameters. Allows setting expiration time or time-to-live (TTL) seconds for cached content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentupdateinputfields.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CachedContentUpdateInputFields {
  expireTime?: string;
  ttlSeconds?: number;
}
```

----------------------------------------

TITLE: Defining systemInstruction Property in GenerativeModel Class (TypeScript)
DESCRIPTION: This code snippet shows the TypeScript signature for the systemInstruction property of the GenerativeModel class. It is an optional property of type Content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generativemodel.systeminstruction.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
systemInstruction?: Content;
```

----------------------------------------

TITLE: Analyzing Gemini API Prompt Feedback
DESCRIPTION: This JSON snippet represents the feedback from the Gemini API regarding a submitted prompt. It provides details on why the prompt might have been blocked and the safety ratings associated with different harm categories. The `probability` field indicates the likelihood of the prompt violating the specified safety category.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-failure-prompt-blocked-safety.txt#2025-04-21_snippet_0

LANGUAGE: json
CODE:
```
{
  "promptFeedback": {
    "blockReason": "SAFETY",
    "safetyRatings": [
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "probability": "NEGLIGIBLE"
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "probability": "HIGH"
      },
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "probability": "NEGLIGIBLE"
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "probability": "NEGLIGIBLE"
      }
    ]
  }
}
```

----------------------------------------

TITLE: Defining CodeExecutionResultPart Interface in TypeScript
DESCRIPTION: This code snippet defines the CodeExecutionResultPart interface, which contains properties related to code execution results. It includes a required codeExecutionResult property and several optional properties.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.codeexecutionresultpart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CodeExecutionResultPart {
  codeExecutionResult: CodeExecutionResult;
  executableCode?: never;
  fileData?: never;
  functionCall?: never;
  functionResponse?: never;
  inlineData?: never;
  text?: never;
}
```

----------------------------------------

TITLE: Defining executableCode Property in TypeScript Interface
DESCRIPTION: Defines an optional executableCode property that is typed as 'never', indicating this property cannot actually contain a value when implemented.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functionresponsepart.executablecode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
executableCode?: never;
```

----------------------------------------

TITLE: Defining Optional Title Property in GroundingChunkWeb
DESCRIPTION: This code snippet defines an optional property 'title' of type string for the GroundingChunkWeb interface. It allows consumers of the interface to optionally specify a title for the chunk. The signature indicates that 'title' can be omitted when implementing the interface.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingchunkweb.title.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
title?: string;
```

----------------------------------------

TITLE: FileMetadata.name property in TypeScript
DESCRIPTION: This code snippet defines the `name` property of the `FileMetadata` interface or class. The `name` property is an optional string, indicated by the `?` symbol. It likely represents the name of a file associated with the `FileMetadata` object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.filemetadata.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
name?: string;
```
```

----------------------------------------

TITLE: Defining the apiKey Property in GoogleAIFileManager Class in TypeScript
DESCRIPTION: TypeScript signature for the apiKey property in the GoogleAIFileManager class, which stores the API key used for authentication with Google AI services.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.googleaifilemanager.apikey.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
apiKey: string;
```

----------------------------------------

TITLE: Defining the SafetySetting Interface in Typescript
DESCRIPTION: Defines the `SafetySetting` interface, which represents the safety settings for content generation. It includes the `category` of harm and the `threshold` for blocking content.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_10

LANGUAGE: typescript
CODE:
```
//@public
export interface SafetySetting {
    // (undocumented)
    category: HarmCategory;
    // (undocumented)
    threshold: HarmBlockThreshold;
}
```

----------------------------------------

TITLE: Defining presencePenalty Property in GenerationConfig Class (TypeScript)
DESCRIPTION: This code snippet defines the presencePenalty property in the GenerationConfig class. It is an optional number that represents the penalty applied to the next token's logprobs if the token has already been seen in the response.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generationconfig.presencepenalty.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
presencePenalty?: number;
```

----------------------------------------

TITLE: SimpleStringSchema Enum Property Declaration
DESCRIPTION: This code snippet shows the declaration of the `enum` property within the `SimpleStringSchema` interface using TypeScript. The `never` type indicates that this property should not be used.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.simplestringschema.enum.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
"enum?: never;"
```

----------------------------------------

TITLE: Defining SimpleStringSchema Type Property
DESCRIPTION: This code snippet defines the 'type' property of the SimpleStringSchema. It is a static property that specifies the type of the schema as 'STRING' using the SchemaType enum. This indicates that the schema is designed to handle string values.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.simplestringschema.type.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
type: typeof SchemaType.STRING;
```
```

----------------------------------------

TITLE: Defining ttlSeconds Property in CachedContentCreateParams Interface (TypeScript)
DESCRIPTION: This code snippet defines the ttlSeconds property in the CachedContentCreateParams interface. It's an optional number property used to specify the time-to-live for CachedContent in seconds. Either this property or expireTime should be specified when creating a CachedContent object.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentcreateparams.ttlseconds.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
ttlSeconds?: number;
```

----------------------------------------

TITLE: Retrieving Detailed Stock Price Information
DESCRIPTION: This snippet details a JSON response regarding the current stock price for Alphabet Inc. (GOOG). It includes the price change percentage and token usage details, indicating its effectiveness in the context of generative AI.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-success-search-grounding.txt#2025-04-21_snippet_1

LANGUAGE: json
CODE:
```
data: {"candidates": [{"content": {"parts": [{"text": " current stock price for Alphabet Inc. (Google) Class C (GOOG)"}], "role": "model"}, "finishReason": "STOP", "index": 0}], "usageMetadata": {"promptTokenCount": 8, "candidatesTokenCount": 17, "totalTokenCount": 25}}
```

----------------------------------------

TITLE: Defining Property for API Key in TypeScript
DESCRIPTION: This snippet defines the apiKey property within the GoogleGenerativeAI class as a string. It's essential for enabling authentication and access to the Google Generative AI services. The property does not have additional dependencies but requires the class to be properly initialized with a valid API key.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeai.apikey.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
apiKey: string;
```

----------------------------------------

TITLE: Defining the updateTime Property in TypeScript for the CachedContent Class
DESCRIPTION: TypeScript definition for the optional updateTime property of the CachedContent class. This property stores the update time of cached content in ISO string format.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontent.updatetime.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
updateTime?: string;
```

----------------------------------------

TITLE: Defining InlineDataPart Interface in TypeScript
DESCRIPTION: TypeScript interface declaration for InlineDataPart that specifies the structure for content parts representing images. Includes optional properties for code execution, function calls, and a required inlineData property of type GenerativeContentBlob.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.inlinedatapart.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface InlineDataPart 
```

----------------------------------------

TITLE: Defining SearchEntryPoint.sdkBlob Property Type in TypeScript
DESCRIPTION: Type definition for the sdkBlob optional property that stores base64 encoded JSON representing an array of search term and search URL tuples.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.searchentrypoint.sdkblob.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
sdkBlob?: string;
```

----------------------------------------

TITLE: Configuring Optional API Client Header in TypeScript
DESCRIPTION: Defines an optional string property for including additional attribution information in the x-goog-api-client header, typically used by wrapper SDKs to provide metadata about the client environment
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.requestoptions.apiclient.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
apiClient?: string;
```

----------------------------------------

TITLE: Defining apiKey Property in GoogleAIFileManager Class (TypeScript)
DESCRIPTION: This code snippet shows the TypeScript signature for the apiKey property in the GoogleAIFileManager class. It is defined as a string type, representing the API key used for authentication with the Google AI services.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaifilemanager.apikey.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
apiKey: string;
```

----------------------------------------

TITLE: Defining the SafetyRating Interface in Typescript
DESCRIPTION: Defines the `SafetyRating` interface, which represents the safety rating for a particular content. It includes the `category` of harm and the `probability` of harm.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/common/api-review/generative-ai.api.md#2025-04-21_snippet_9

LANGUAGE: typescript
CODE:
```
//@public
export interface SafetyRating {
    // (undocumented)
    category: HarmCategory;
    // (undocumented)
    probability: HarmProbability;
}
```

----------------------------------------

TITLE: Defining Custom Error Class for Google Generative AI
DESCRIPTION: Extends the standard Error class to create a specialized error type for the Google Generative AI SDK, allowing for more precise error handling and differentiation from generic JavaScript errors
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.googlegenerativeaierror.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export declare class GoogleGenerativeAIError extends Error
```

----------------------------------------

TITLE: Defining ListParams.pageToken Property in TypeScript
DESCRIPTION: This code snippet defines the 'pageToken' property in TypeScript. It is part of the ListParams structure and is utilized to handle pagination in API requests for the Google Generative AI JavaScript library. The property is optional and accepts a string value representing a token for fetching subsequent pages of results. Prerequisites include understanding of TypeScript optional properties and API pagination conventions.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/files/generative-ai.listparams.pagetoken.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
pageToken?: string;
```

----------------------------------------

TITLE: Defining Integer Schema Format in TypeScript
DESCRIPTION: Specifies an optional format property for integer schemas that can be either 32-bit or 64-bit integers. This allows precise type definition and range specification.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.integerschema.format.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
format?: "int32" | "int64";
```

----------------------------------------

TITLE: Defining contents Property Type in TypeScript
DESCRIPTION: Type definition for the contents property in the CachedContentBase class, representing an array of Content objects.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.cachedcontentbase.contents.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
contents: Content[];
```

----------------------------------------

TITLE: Providing Timestamp for Stock Price Data
DESCRIPTION: This snippet includes a JSON structure that specifies the timestamp for the stock price response, emphasizing the importance of date and time in financial statistics.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-success-search-grounding.txt#2025-04-21_snippet_4

LANGUAGE: json
CODE:
```
data: {"candidates": [{"content": {"parts": [{"text": " October 2, 2024, at 5:58 PM UTC.  You can find the most up-to-date information on"}], "role": "model"}, "finishReason": "STOP", "index": 0}], "usageMetadata": {"promptTokenCount": 8, "candidatesTokenCount": 97, "totalTokenCount": 105}}
```

----------------------------------------

TITLE: Defining GenerateContentStreamResult Response Promise
DESCRIPTION: Declares a Promise that resolves to an EnhancedGenerateContentResponse, providing asynchronous access to generated content stream results
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.generatecontentstreamresult.response.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
response: Promise<EnhancedGenerateContentResponse>;
```

----------------------------------------

TITLE: Defining executableCode Property in InlineDataPart Interface (TypeScript)
DESCRIPTION: Declares the executableCode property as an optional member of the InlineDataPart interface. The type is set to 'never', suggesting this property should not be used or assigned a value in implementations.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.inlinedatapart.executablecode.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
executableCode?: never;
```

----------------------------------------

TITLE: CodeExecutionTool Interface Definition
DESCRIPTION: Defines the CodeExecutionTool interface in TypeScript. This interface is used to enable code execution within the Generative AI model. The `codeExecution` property is an empty object that signals the capability to execute code and may have subfields added in the future.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.codeexecutiontool.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export interface CodeExecutionTool 
```

----------------------------------------

TITLE: Defining FunctionDeclaration Name Property Type in TypeScript
DESCRIPTION: Type definition for the name property of a FunctionDeclaration. The name must start with a letter or underscore, can only contain alphanumeric characters, underscores, and dashes, with a maximum length of 64 characters.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.functiondeclaration.name.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
name: string;
```

----------------------------------------

TITLE: Deleting Content Cache in GoogleAICacheManager with TypeScript
DESCRIPTION: Method signature for deleting content from the cache using a specified name. The method accepts a string name parameter and returns a Promise that resolves to void when the deletion is complete.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.googleaicachemanager.delete.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
delete(name: string): Promise<void>;
```

----------------------------------------

TITLE: Defining values Property in TypeScript
DESCRIPTION: This snippet defines the 'values' property within the ContentEmbedding class as an array of numbers, which indicates that it holds multiple numerical values for some form of embedding content. This property facilitates the representation of complex data structures where numerical values are essential.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.contentembedding.values.md#2025-04-21_snippet_0

LANGUAGE: TypeScript
CODE:
```
values: number[];
```

----------------------------------------

TITLE: Defining webSearchQueries Property in TypeScript
DESCRIPTION: This code snippet defines the `webSearchQueries` property as a string array within the `GroundingMetadata` class.  It indicates that the property is intended to hold a list of search queries.  These queries can be utilized for performing follow-up web searches, likely related to grounding or enhancing the generative AI model's responses.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingmetadata.websearchqueries.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
```typescript
webSearchQueries: string[];
```
```

----------------------------------------

TITLE: Defining RpcStatus.message Property in TypeScript
DESCRIPTION: This code snippet defines a property 'message' of type string in the RpcStatus interface, intended to represent a developer-facing error message. The property is crucial for error handling and provides a way to convey specific error details to developers. It requires a context where RpcStatus is utilized to structure response messages appropriately.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/server/generative-ai.rpcstatus.message.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
message: string;
```

----------------------------------------

TITLE: Defining groundingChunckIndices Property in TypeScript
DESCRIPTION: This snippet defines the groundingChunckIndices property as an optional array of numbers. It is used to specify indices that point to the relevant 'grounding_chunk' elements which are the citations related to a specific claim.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.groundingsupport.groundingchunckindices.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
groundingChunckIndices?: number[];
```

----------------------------------------

TITLE: Including Stock Price Change Warning
DESCRIPTION: This snippet features a JSON response expressing a warning regarding the rapid changes in stock prices. It reinforces the necessity of current data and includes token usage statistics.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/test-utils/mock-responses/streaming-success-search-grounding.txt#2025-04-21_snippet_3

LANGUAGE: json
CODE:
```
data: {"candidates": [{"content": {"parts": [{"text": " -0.97% over the last 24 hours. \n\nPlease note that stock prices can change rapidly.  This information is current as of"}], "role": "model"}, "finishReason": "STOP", "index": 0}], "usageMetadata": {"promptTokenCount": 8, "candidatesTokenCount": 65, "totalTokenCount": 73}}
```

----------------------------------------

TITLE: Defining FunctionDeclarationSchemaProperty Type in TypeScript
DESCRIPTION: Type definition for the FunctionDeclarationSchemaProperty which represents the schema for top-level function declarations. It's a direct alias to the Schema type.
SOURCE: https://github.com/google-gemini/generative-ai-js/blob/main/docs/reference/main/generative-ai.functiondeclarationschemaproperty.md#2025-04-21_snippet_0

LANGUAGE: typescript
CODE:
```
export type FunctionDeclarationSchemaProperty = Schema;
```