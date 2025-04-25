TITLE: Initializing with Gemini Developer API Key
DESCRIPTION: Code snippet showing how to initialize the SDK for server-side applications using an API key from Google AI Studio. This is the standard way to authenticate with the Gemini Developer API.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_2

LANGUAGE: typescript
CODE:
```
import { GoogleGenAI } from '@google/genai';
const ai = new GoogleGenAI({apiKey: 'GEMINI_API_KEY'});
```

----------------------------------------

TITLE: Basic Content Generation with Gemini API
DESCRIPTION: Simple example demonstrating how to initialize the SDK with an API key and generate content using the Gemini model. This code asks a simple question and logs the response text.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_1

LANGUAGE: typescript
CODE:
```
import {GoogleGenAI} from '@google/genai';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const ai = new GoogleGenAI({apiKey: GEMINI_API_KEY});

async function main() {
  const response = await ai.models.generateContent({
    model: 'gemini-2.0-flash-001',
    contents: 'Why is the sky blue?',
  });
  console.log(response.text);
}

main();
```

----------------------------------------

TITLE: Function Calling with Gemini API
DESCRIPTION: Implementation of function calling to allow Gemini to interact with external systems. This example defines a light control function, sends a prompt to Gemini, and retrieves the function call parameters that Gemini decides to use.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_6

LANGUAGE: typescript
CODE:
```
import {GoogleGenAI, FunctionCallingConfigMode, FunctionDeclaration, Type} from '@google/genai';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

async function main() {
  const controlLightDeclaration: FunctionDeclaration = {
    name: 'controlLight',
    parameters: {
      type: Type.OBJECT,
      description: 'Set the brightness and color temperature of a room light.',
      properties: {
        brightness: {
          type: Type.NUMBER,
          description:
              'Light level from 0 to 100. Zero is off and 100 is full brightness.',
        },
        colorTemperature: {
          type: Type.STRING,
          description:
              'Color temperature of the light fixture which can be `daylight`, `cool`, or `warm`.',
        },
      },
      required: ['brightness', 'colorTemperature'],
    },
  };

  const ai = new GoogleGenAI({apiKey: GEMINI_API_KEY});
  const response = await ai.models.generateContent({
    model: 'gemini-2.0-flash-001',
    contents: 'Dim the lights so the room feels cozy and warm.',
    config: {
      toolConfig: {
        functionCallingConfig: {
          // Force it to call any function
          mode: FunctionCallingConfigMode.ANY,
          allowedFunctionNames: ['controlLight'],
        }
      },
      tools: [{functionDeclarations: [controlLightDeclaration]}]
    }
  });

  console.log(response.functionCalls);
}

main();
```

----------------------------------------

TITLE: Installing Google Gen AI SDK with npm
DESCRIPTION: Command to install the Google Gen AI SDK package using npm. This is the first step to integrate Gemini capabilities into your JavaScript or TypeScript project.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_0

LANGUAGE: shell
CODE:
```
npm install @google/genai
```

----------------------------------------

TITLE: Core TypeScript Interfaces and Enums
DESCRIPTION: Core type definitions for the Google AI API including interfaces for model configuration, content generation parameters, and response types. Includes enums for modes, outcomes, and media types.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_44

LANGUAGE: typescript
CODE:
```
export interface Model {
    description?: string;
    displayName?: string;
    endpoints?: Endpoint[];
    inputTokenLimit?: number;
    labels?: Record<string, string>;
    name?: string;
    outputTokenLimit?: number;
    supportedActions?: string[];
    tunedModelInfo?: TunedModelInfo;
    version?: string;
}

export enum MediaModality {
    AUDIO = "AUDIO",
    DOCUMENT = "DOCUMENT",
    IMAGE = "IMAGE",
    MODALITY_UNSPECIFIED = "MODALITY_UNSPECIFIED",
    TEXT = "TEXT",
    VIDEO = "VIDEO"
}
```

----------------------------------------

TITLE: Streaming Content Generation from Gemini
DESCRIPTION: Example of using the streaming API to get content chunks as they're generated, providing a more responsive user experience. This code generates a poem and prints each chunk as it arrives.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_5

LANGUAGE: typescript
CODE:
```
import {GoogleGenAI} from '@google/genai';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const ai = new GoogleGenAI({apiKey: GEMINI_API_KEY});

async function main() {
  const response = await ai.models.generateContentStream({
    model: 'gemini-2.0-flash-001',
    contents: 'Write a 100-word poem.',
  });
  for await (const chunk of response) {
    console.log(chunk.text);
  }
}

main();
```

----------------------------------------

TITLE: TypeScript Interface and Type Definitions for Google GenAI API
DESCRIPTION: Comprehensive type definitions and interfaces for the Google GenAI API client library. Includes types for authentication, content generation, chat functionality, embeddings, and file operations.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_0

LANGUAGE: typescript
CODE:
```
import { GoogleAuthOptions } from 'google-auth-library';

// @public
export interface ActivityEnd {
}

// @public
export enum ActivityHandling {
    // (undocumented)
    ACTIVITY_HANDLING_UNSPECIFIED = "ACTIVITY_HANDLING_UNSPECIFIED",
    // (undocumented)
    NO_INTERRUPTION = "NO_INTERRUPTION",
    // (undocumented) 
    START_OF_ACTIVITY_INTERRUPTS = "START_OF_ACTIVITY_INTERRUPTS"
}

// @public
export interface ActivityStart {
}

// Additional interfaces and types omitted for brevity...
```

----------------------------------------

TITLE: Implementing GoogleGenAI Class in TypeScript
DESCRIPTION: This class represents the main entry point for interacting with the Google GenAI API. It includes properties for various API functionalities and takes GoogleGenAIOptions as a constructor parameter.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_41

LANGUAGE: TypeScript
CODE:
```
// @public
export class GoogleGenAI {
    constructor(options: GoogleGenAIOptions);
    // (undocumented)
    protected readonly apiClient: ApiClient;
    // (undocumented)
    readonly caches: Caches;
    // (undocumented)
    readonly chats: Chats;
    // (undocumented)
    readonly files: Files;
    // (undocumented)
    readonly live: Live;
    // (undocumented)
    readonly models: Models;
    // (undocumented)
    readonly operations: Operations;
    // (undocumented)
    readonly vertexai: boolean;
}
```

----------------------------------------

TITLE: GoogleGenAI Class Definition
DESCRIPTION: Main class for interacting with Google's Generative AI services. Handles initialization of API clients and provides access to various service endpoints.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_5

LANGUAGE: typescript
CODE:
```
export class GoogleGenAI {
    constructor(options: GoogleGenAIOptions);
    protected readonly apiClient: ApiClient;
    readonly caches: Caches;
    readonly chats: Chats;
    readonly files: Files;
    readonly live: Live;
    readonly models: Models;
    readonly operations: Operations;
    readonly vertexai: boolean;
}
```

----------------------------------------

TITLE: TypeScript API Definitions for @google/genai
DESCRIPTION: Comprehensive TypeScript type definitions for the Google Generative AI client library, including interfaces, enums, and classes for working with generative AI models, chats, caches, and related functionality.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_0

LANGUAGE: typescript
CODE:
```
import { GoogleAuthOptions } from 'google-auth-library';

// @public
export interface ActivityEnd {
}

// @public
export enum ActivityHandling {
    // (undocumented)
    ACTIVITY_HANDLING_UNSPECIFIED = "ACTIVITY_HANDLING_UNSPECIFIED",
    // (undocumented)
    NO_INTERRUPTION = "NO_INTERRUPTION",
    // (undocumented)
    START_OF_ACTIVITY_INTERRUPTS = "START_OF_ACTIVITY_INTERRUPTS"
}

// @public
export interface ActivityStart {
}

// @public
export interface AudioTranscriptionConfig {
}

// @public
export interface AutomaticActivityDetection {
    disabled?: boolean;
    endOfSpeechSensitivity?: EndSensitivity;
    prefixPaddingMs?: number;
    silenceDurationMs?: number;
    startOfSpeechSensitivity?: StartSensitivity;
}

// @public
export interface BaseUrlParameters {
    // (undocumented)
    geminiUrl?: string;
    // (undocumented)
    vertexUrl?: string;
}

// @public
interface Blob_2 {
    data?: string;
    mimeType?: string;
}
export { Blob_2 as Blob }

// @public (undocumented)
export type BlobImageUnion = Blob_2;

// @public
export enum BlockedReason {
    // (undocumented)
    BLOCKED_REASON_UNSPECIFIED = "BLOCKED_REASON_UNSPECIFIED",
    // (undocumented)
    BLOCKLIST = "BLOCKLIST",
    // (undocumented)
    OTHER = "OTHER",
    // (undocumented)
    PROHIBITED_CONTENT = "PROHIBITED_CONTENT",
    // (undocumented)
    SAFETY = "SAFETY"
}

// @public
export interface CachedContent {
    createTime?: string;
    displayName?: string;
    expireTime?: string;
    model?: string;
    name?: string;
    updateTime?: string;
    usageMetadata?: CachedContentUsageMetadata;
}

// @public
export interface CachedContentUsageMetadata {
    audioDurationSeconds?: number;
    imageCount?: number;
    textCount?: number;
    totalTokenCount?: number;
    videoDurationSeconds?: number;
}

// Warning: (ae-forgotten-export) The symbol "BaseModule" needs to be exported by the entry point index.d.ts
//
// @public (undocumented)
export class Caches extends BaseModule {
    // Warning: (ae-forgotten-export) The symbol "ApiClient" needs to be exported by the entry point index.d.ts
    constructor(apiClient: ApiClient);
    create(params: types.CreateCachedContentParameters): Promise<types.CachedContent>;
    delete(params: types.DeleteCachedContentParameters): Promise<types.DeleteCachedContentResponse>;
    get(params: types.GetCachedContentParameters): Promise<types.CachedContent>;
    // Warning: (ae-forgotten-export) The symbol "types" needs to be exported by the entry point index.d.ts
    list: (params?: types.ListCachedContentsParameters) => Promise<Pager<types.CachedContent>>;
    update(params: types.UpdateCachedContentParameters): Promise<types.CachedContent>;
}

// @public
export interface Candidate {
    avgLogprobs?: number;
    citationMetadata?: CitationMetadata;
    content?: Content;
    finishMessage?: string;
    finishReason?: FinishReason;
    groundingMetadata?: GroundingMetadata;
    index?: number;
    logprobsResult?: LogprobsResult;
    safetyRatings?: SafetyRating[];
    tokenCount?: number;
}

// @public
export class Chat {
    constructor(apiClient: ApiClient, modelsModule: Models, model: string, config?: types.GenerateContentConfig, history?: types.Content[]);
    getHistory(curated?: boolean): types.Content[];
    sendMessage(params: types.SendMessageParameters): Promise<types.GenerateContentResponse>;
    sendMessageStream(params: types.SendMessageParameters): Promise<AsyncGenerator<types.GenerateContentResponse>>;
}

// @public
export class Chats {
    constructor(modelsModule: Models, apiClient: ApiClient);
    create(params: types.CreateChatParameters): Chat;
}

// @public
export interface Citation {
    endIndex?: number;
    license?: string;
    publicationDate?: GoogleTypeDate;
    startIndex?: number;
    title?: string;
    uri?: string;
}

// @public
export interface CitationMetadata {
    citations?: Citation[];
}

// @public
export interface CodeExecutionResult {
    outcome?: Outcome;
    output?: string;
}

// @public
export interface ComputeTokensConfig {
    abortSignal?: AbortSignal;
    httpOptions?: HttpOptions;
}

// @public
export interface ComputeTokensParameters {
    config?: ComputeTokensConfig;
    contents: ContentListUnion;
    model: string;
}

// @public
export class ComputeTokensResponse {
    tokensInfo?: TokensInfo[];
}

// @public
export interface Content {
    parts?: Part[];
    role?: string;
}

// @public
export interface ContentEmbedding {
    statistics?: ContentEmbeddingStatistics;
    values?: number[];
}

// @public
export interface ContentEmbeddingStatistics {
    tokenCount?: number;
    truncated?: boolean;
}

// @public (undocumented)
export type ContentListUnion = Content | Content[] | PartUnion | PartUnion[];

// @public (undocumented)
export type ContentUnion = Content | PartUnion[] | PartUnion;

// @public
export interface ContextWindowCompressionConfig {
    slidingWindow?: SlidingWindow;
    triggerTokens?: string;
}

// @public
export interface ControlReferenceConfig {
    controlType?: ControlReferenceType;
    enableControlImageComputation?: boolean;
}

// @public
export interface ControlReferenceImage {
    config?: ControlReferenceConfig;
    referenceId?: number;
    referenceImage?: Image_2;
    referenceType?: string;
}

// @public
export enum ControlReferenceType {
    // (undocumented)
    CONTROL_TYPE_CANNY = "CONTROL_TYPE_CANNY",
    // (undocumented)
    CONTROL_TYPE_DEFAULT = "CONTROL_TYPE_DEFAULT",
    // (undocumented)
    CONTROL_TYPE_FACE_MESH = "CONTROL_TYPE_FACE_MESH",
    // (undocumented)
    CONTROL_TYPE_SCRIBBLE = "CONTROL_TYPE_SCRIBBLE"
}

// @public
export interface CountTokensConfig {
    abortSignal?: AbortSignal;
    generationConfig?: GenerationConfig;
    httpOptions?: HttpOptions;
    systemInstruction?: ContentUnion;
    tools?: Tool[];
}

// @public
export interface CountTokensParameters {
    config?: CountTokensConfig;
    contents: ContentListUnion;
    model: string;
}

// @public
export class CountTokensResponse {
    cachedContentTokenCount?: number;
    totalTokens?: number;
}

// @public
export interface CreateCachedContentConfig {
    abortSignal?: AbortSignal;
    contents?: ContentListUnion;
    displayName?: string;
    expireTime?: string;
    httpOptions?: HttpOptions;
    systemInstruction?: ContentUnion;
    toolConfig?: ToolConfig;
    tools?: Tool[];
    ttl?: string;
}

// @public
export interface CreateCachedContentParameters {
    config?: CreateCachedContentConfig;
    model: string;
}

// @public
export interface CreateChatParameters {
    config?: GenerateContentConfig;
    history?: Content[];
    model: string;
}

// @public
export interface CreateFileConfig {
    abortSignal?: AbortSignal;
    httpOptions?: HttpOptions;
}

// @public
export interface CreateFileParameters {
    config?: CreateFileConfig;
    file: File_2;
}

// @public
export class CreateFileResponse {
    sdkHttpResponse?: HttpResponse;
}

// @public
export function createModelContent(partOrString: PartListUnion | string): Content;

// @public
export function createPartFromBase64(data: string, mimeType: string): Part;

// @public
export function createPartFromCodeExecutionResult(outcome: Outcome, output: string): Part;

// @public
export function createPartFromExecutableCode(code: string, language: Language): Part;

// @public
export function createPartFromFunctionCall(name: string, args: Record<string, unknown>): Part;

// @public
export function createPartFromFunctionResponse(id: string, name: string, response: Record<string, unknown>): Part;

// @public
export function createPartFromText(text: string): Part;

// @public
export function createPartFromUri(uri: string, mimeType: string): Part;

// @public
export function createUserContent(partOrString: PartListUnion | string): Content;

// @public
export interface DeleteCachedContentConfig {
    abortSignal?: AbortSignal;
    httpOptions?: HttpOptions;
}

// @public
export interface DeleteCachedContentParameters {
    config?: DeleteCachedContentConfig;
    name: string;
}

// @public
export class DeleteCachedContentResponse {
}

// @public
export interface DeleteFileConfig {
    abortSignal?: AbortSignal;
    httpOptions?: HttpOptions;
}

// @public
export interface DeleteFileParameters {
    config?: DeleteFileConfig;
    name: string;
}

// @public
export class DeleteFileResponse {
}

// @public
export interface DownloadFileConfig {
    abortSignal?: AbortSignal;
    httpOptions?: HttpOptions;
}

// @public
export interface DynamicRetrievalConfig {
    dynamicThreshold?: number;
    mode?: DynamicRetrievalConfigMode;
}

// @public
export enum DynamicRetrievalConfigMode {
    // (undocumented)
    MODE_DYNAMIC = "MODE_DYNAMIC",
    // (undocumented)
    MODE_UNSPECIFIED = "MODE_UNSPECIFIED"
}

// @public (undocumented)
export interface EmbedContentConfig {
    abortSignal?: AbortSignal;
    autoTruncate?: boolean;
    httpOptions?: HttpOptions;
    mimeType?: string;
    outputDimensionality?: number;
    taskType?: string;
    title?: string;
}

// @public
export interface EmbedContentMetadata {
    billableCharacterCount?: number;
}

// @public
export interface EmbedContentParameters {
    config?: EmbedContentConfig;
    contents: ContentListUnion;
    model: string;
}

// @public
export class EmbedContentResponse {
    embeddings?: ContentEmbedding[];
    metadata?: EmbedContentMetadata;
}

// @public
```

----------------------------------------

TITLE: Defining Google GenAI Client Class in TypeScript
DESCRIPTION: Defines the main GoogleGenAI class for interacting with Google's Generative AI API. It includes properties for different API functionalities and a constructor that accepts GoogleGenAIOptions.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_40

LANGUAGE: TypeScript
CODE:
```
// @public
export class GoogleGenAI {
    constructor(options: GoogleGenAIOptions);
    // (undocumented)
    protected readonly apiClient: ApiClient;
    // (undocumented)
    readonly caches: Caches;
    // (undocumented)
    readonly chats: Chats;
    // (undocumented)
    readonly files: Files;
    // (undocumented)
    readonly live: Live;
    // (undocumented)
    readonly models: Models;
    // (undocumented)
    readonly operations: Operations;
    // (undocumented)
    readonly vertexai: boolean;
}
```

----------------------------------------

TITLE: Defining Google GenAI Options Interface in TypeScript
DESCRIPTION: Specifies the options for initializing the GoogleGenAI client, including API key, version, authentication options, and other configuration parameters.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_41

LANGUAGE: TypeScript
CODE:
```
// @public
export interface GoogleGenAIOptions {
    apiKey?: string;
    apiVersion?: string;
    googleAuthOptions?: GoogleAuthOptions;
    httpOptions?: HttpOptions;
    location?: string;
    project?: string;
    vertexai?: boolean;
}
```

----------------------------------------

TITLE: Defining GoogleGenAIOptions Interface in TypeScript
DESCRIPTION: This interface specifies the configuration options for initializing the GoogleGenAI class. It includes properties for API key, version, authentication options, and other settings.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_42

LANGUAGE: TypeScript
CODE:
```
// @public
export interface GoogleGenAIOptions {
    apiKey?: string;
    apiVersion?: string;
    googleAuthOptions?: GoogleAuthOptions;
    httpOptions?: HttpOptions;
    location?: string;
    project?: string;
    vertexai?: boolean;
}
```

----------------------------------------

TITLE: Initializing with Vertex AI Configuration
DESCRIPTION: Sample code for initializing the SDK with Vertex AI instead of the Gemini Developer API. This requires specifying the Google Cloud project and location parameters.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_4

LANGUAGE: typescript
CODE:
```
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({
    vertexai: true,
    project: 'your_project',
    location: 'your_location',
});
```

----------------------------------------

TITLE: TypeScript Interface and Type Definitions for Google GenAI
DESCRIPTION: Core type definitions and interfaces for the Google GenAI library, including enums for activity handling, interfaces for content generation, and classes for chat functionality.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_0

LANGUAGE: typescript
CODE:
```
import { GoogleAuthOptions } from 'google-auth-library';

// @public
export interface ActivityEnd {
}

// @public
export enum ActivityHandling {
    // (undocumented)
    ACTIVITY_HANDLING_UNSPECIFIED = "ACTIVITY_HANDLING_UNSPECIFIED",
    // (undocumented)
    NO_INTERRUPTION = "NO_INTERRUPTION",
    // (undocumented)
    START_OF_ACTIVITY_INTERRUPTS = "START_OF_ACTIVITY_INTERRUPTS"
}
```

----------------------------------------

TITLE: Live Class Implementation
DESCRIPTION: Class handling live/real-time interactions with the GenAI service, including WebSocket connections and session management.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_7

LANGUAGE: typescript
CODE:
```
export class Live {
    constructor(apiClient: ApiClient, auth: Auth, webSocketFactory: WebSocketFactory);
    connect(params: types.LiveConnectParameters): Promise<Session>;
}
```

----------------------------------------

TITLE: Model Operations Class Definition
DESCRIPTION: Class definition for Models that extends BaseModule, providing methods for generating content, images, videos and computing tokens.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_45

LANGUAGE: typescript
CODE:
```
export class Models extends BaseModule {
    constructor(apiClient: ApiClient);
    computeTokens(params: types.ComputeTokensParameters): Promise<types.ComputeTokensResponse>;
    countTokens(params: types.CountTokensParameters): Promise<types.CountTokensResponse>;
    embedContent(params: types.EmbedContentParameters): Promise<types.EmbedContentResponse>;
    generateContent: (params: types.GenerateContentParameters) => Promise<types.GenerateContentResponse>;
    generateContentStream: (params: types.GenerateContentParameters) => Promise<AsyncGenerator<types.GenerateContentResponse>>;
    generateImages: (params: types.GenerateImagesParameters) => Promise<types.GenerateImagesResponse>;
    generateVideos(params: types.GenerateVideosParameters): Promise<types.GenerateVideosOperation>;
    get(params: types.GetModelParameters): Promise<types.Model>;
}
```

----------------------------------------

TITLE: Class Definition - Files Module
DESCRIPTION: Class implementation for file operations including upload, download, listing and deletion
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_3

LANGUAGE: typescript
CODE:
```
export class Files extends BaseModule {
    constructor(apiClient: ApiClient);
    delete(params: types.DeleteFileParameters): Promise<types.DeleteFileResponse>;
    get(params: types.GetFileParameters): Promise<types.File>;
    list: (params?: types.ListFilesParameters) => Promise<Pager<types.File>>;
    upload(params: types.UploadFileParameters): Promise<types.File>;
}
```

----------------------------------------

TITLE: Defining Model Interface in TypeScript
DESCRIPTION: Defines an interface for models, including properties such as name, description, endpoints, token limits, and supported actions.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_23

LANGUAGE: TypeScript
CODE:
```
// @public
export interface Model {
    description?: string;
    displayName?: string;
    endpoints?: Endpoint[];
    inputTokenLimit?: number;
    labels?: Record<string, string>;
    name?: string;
    outputTokenLimit?: number;
    supportedActions?: string[];
    tunedModelInfo?: TunedModelInfo;
    version?: string;
}
```

----------------------------------------

TITLE: Defining Models Class in TypeScript
DESCRIPTION: Defines a class for model-related operations, including methods for computing tokens, generating content, and generating images.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_61

LANGUAGE: TypeScript
CODE:
```
// @public (undocumented)
export class Models extends BaseModule {
    constructor(apiClient: ApiClient);
    computeTokens(params: types.ComputeTokensParameters): Promise<types.ComputeTokensResponse>;
    countTokens(params: types.CountTokensParameters): Promise<types.CountTokensResponse>;
    embedContent(params: types.EmbedContentParameters): Promise<types.EmbedContentResponse>;
    generateContent: (params: types.GenerateContentParameters) => Promise<types.GenerateContentResponse>;
    generateContentStream: (params: types.GenerateContentParameters) => Promise<AsyncGenerator<types.GenerateContentResponse>>;
    generateImages: (params: types.GenerateImagesParameters) => Promise<types.GenerateImagesResponse>;
    generateVideos(params: types.GenerateVideosParameters): Promise<types.GenerateVideosOperation>;
    get(params: types.GetModelParameters): Promise<types.Model>;
}
```

----------------------------------------

TITLE: Setting Environment Variables for Google GenAI SDK
DESCRIPTION: Environment variable configuration required for the samples to authenticate with Gemini API and Google Cloud. These must be set before running any samples.
SOURCE: https://github.com/googleapis/js-genai/blob/main/sdk-samples/README.md#2025-04-23_snippet_1

LANGUAGE: sh
CODE:
```
export GEMINI_API_KEY=<GEMINI_KEY>
export GOOGLE_CLOUD_PROJECT=<GOOGLE_CLOUD_PROJECT>
export GOOGLE_CLOUD_LOCATION=<GCP_REGION>
```

----------------------------------------

TITLE: Defining FunctionDeclaration Interface in TypeScript
DESCRIPTION: Interface for declaring functions available to the model, including description, name, input parameters, and response schema.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_17

LANGUAGE: typescript
CODE:
```
// @public
export interface FunctionDeclaration {
    description?: string;
    name?: string;
    parameters?: Schema;
    response?: Schema;
}
```

----------------------------------------

TITLE: Defining Models Class in TypeScript
DESCRIPTION: Defines a class for interacting with models, including methods for computing tokens, generating content, and retrieving model information.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_24

LANGUAGE: TypeScript
CODE:
```
// @public (undocumented)
export class Models extends BaseModule {
    constructor(apiClient: ApiClient);
    computeTokens(params: types.ComputeTokensParameters): Promise<types.ComputeTokensResponse>;
    countTokens(params: types.CountTokensParameters): Promise<types.CountTokensResponse>;
    embedContent(params: types.EmbedContentParameters): Promise<types.EmbedContentResponse>;
    generateContent: (params: types.GenerateContentParameters) => Promise<types.GenerateContentResponse>;
    generateContentStream: (params: types.GenerateContentParameters) => Promise<AsyncGenerator<types.GenerateContentResponse>>;
    generateImages: (params: types.GenerateImagesParameters) => Promise<types.GenerateImagesResponse>;
    generateVideos(params: types.GenerateVideosParameters): Promise<types.GenerateVideosOperation>;
    get(params: types.GetModelParameters): Promise<types.Model>;
}
```

----------------------------------------

TITLE: Implementing Session Class in TypeScript
DESCRIPTION: Defines a Session class for managing WebSocket connections and API client interactions, including methods for sending various types of content.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_91

LANGUAGE: TypeScript
CODE:
```
export class Session {
    constructor(conn: WebSocket_2, apiClient: ApiClient);
    close(): void;
    readonly conn: WebSocket_2;
    sendClientContent(params: types.LiveSendClientContentParameters): void;
    sendRealtimeInput(params: types.LiveSendRealtimeInputParameters): void;
    sendToolResponse(params: types.LiveSendToolResponseParameters): void;
}
```

----------------------------------------

TITLE: Defining FunctionCallingConfigMode Enum in TypeScript
DESCRIPTION: Enumeration of function calling modes: AUTO, ANY, NONE, or UNSPECIFIED. Controls how the model uses function calling capabilities.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_16

LANGUAGE: typescript
CODE:
```
// @public
export enum FunctionCallingConfigMode {
    // (undocumented)
    ANY = "ANY",
    // (undocumented)
    AUTO = "AUTO",
    // (undocumented)
    MODE_UNSPECIFIED = "MODE_UNSPECIFIED",
    // (undocumented)
    NONE = "NONE"
}
```

----------------------------------------

TITLE: Defining LiveConnectParameters Interface in TypeScript
DESCRIPTION: This interface specifies the parameters required for connecting to a live session. It includes callbacks for handling various events, configuration options, and the model to use.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_44

LANGUAGE: TypeScript
CODE:
```
// @public
export interface LiveConnectParameters {
    callbacks: LiveCallbacks;
    config?: LiveConnectConfig;
    model: string;
}
```

----------------------------------------

TITLE: Implementing GenerateContentResponse Class in TypeScript
DESCRIPTION: Defines a GenerateContentResponse class with various properties and getter methods for accessing generated content and metadata.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_21

LANGUAGE: typescript
CODE:
```
export class GenerateContentResponse {
    candidates?: Candidate[];
    get codeExecutionResult(): string | undefined;
    createTime?: string;
    get data(): string | undefined;
    get executableCode(): string | undefined;
    get functionCalls(): FunctionCall[] | undefined;
    modelVersion?: string;
    promptFeedback?: GenerateContentResponsePromptFeedback;
    responseId?: string;
    get text(): string | undefined;
    usageMetadata?: GenerateContentResponseUsageMetadata;
}
```

----------------------------------------

TITLE: Pager Implementation
DESCRIPTION: Generic Pager class implementation for handling paginated responses from the API, with async iterator support.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_46

LANGUAGE: typescript
CODE:
```
export class Pager<T> implements AsyncIterable<T> {
    [Symbol.asyncIterator](): AsyncIterator<T>;
    constructor(name: PagedItem, request: (params: PagedItemConfig) => Promise<PagedItemResponse<T>>, response: PagedItemResponse<T>, params: PagedItemConfig);
    getItem(index: number): T;
    hasNextPage(): boolean;
    protected idxInternal: number;
    get name(): PagedItem;
    nextPage(): Promise<T[]>;
    get page(): T[];
    get pageLength(): number;
    get pageSize(): number;
    get params(): PagedItemConfig;
    protected requestInternal: (params: PagedItemConfig) => Promise<PagedItemResponse<T>>;
}
```

----------------------------------------

TITLE: Defining Safety Rating Interface in TypeScript
DESCRIPTION: TypeScript interface defining the structure of safety ratings returned by the AI model. It includes properties for blocked status, harm category, probability, and severity measures.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_47

LANGUAGE: typescript
CODE:
```
// @public
export interface SafetyRating {
    blocked?: boolean;
    category?: HarmCategory;
    probability?: HarmProbability;
    probabilityScore?: number;
    severity?: HarmSeverity;
    severityScore?: number;
}
```

----------------------------------------

TITLE: Defining Live Class for Real-time Interactions in TypeScript
DESCRIPTION: Implements the Live class for real-time interactions with the API, including methods for connecting and handling live sessions.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_42

LANGUAGE: TypeScript
CODE:
```
// @public
export class Live {
    // Warning: (ae-forgotten-export) The symbol "Auth" needs to be exported by the entry point index.d.ts
    // Warning: (ae-forgotten-export) The symbol "WebSocketFactory" needs to be exported by the entry point index.d.ts
    constructor(apiClient: ApiClient, auth: Auth, webSocketFactory: WebSocketFactory);
    connect(params: types.LiveConnectParameters): Promise<Session>;
}
```

----------------------------------------

TITLE: Implementing GenerateContentResponse Class in TypeScript
DESCRIPTION: Class representing a response from content generation with candidates, metadata, and convenience getters for accessing text, code, and function calls.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_21

LANGUAGE: typescript
CODE:
```
// @public
export class GenerateContentResponse {
    candidates?: Candidate[];
    get codeExecutionResult(): string | undefined;
    createTime?: string;
    get data(): string | undefined;
    get executableCode(): string | undefined;
    get functionCalls(): FunctionCall[] | undefined;
    modelVersion?: string;
    promptFeedback?: GenerateContentResponsePromptFeedback;
    responseId?: string;
    get text(): string | undefined;
    usageMetadata?: GenerateContentResponseUsageMetadata;
}
```

----------------------------------------

TITLE: Defining GenerateContentConfig Interface in TypeScript
DESCRIPTION: Comprehensive interface for configuring content generation with numerous optional parameters including safety settings, temperature, and token limits.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_19

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateContentConfig {
    abortSignal?: AbortSignal;
    audioTimestamp?: boolean;
    cachedContent?: string;
    candidateCount?: number;
    frequencyPenalty?: number;
    httpOptions?: HttpOptions;
    labels?: Record<string, string>;
    logprobs?: number;
    maxOutputTokens?: number;
    mediaResolution?: MediaResolution;
    modelSelectionConfig?: ModelSelectionConfig;
    presencePenalty?: number;
    responseLogprobs?: boolean;
    responseMimeType?: string;
    responseModalities?: string[];
    responseSchema?: SchemaUnion;
    routingConfig?: GenerationConfigRoutingConfig;
    safetySettings?: SafetySetting[];
    seed?: number;
    speechConfig?: SpeechConfigUnion;
    stopSequences?: string[];
    systemInstruction?: ContentUnion;
    temperature?: number;
    thinkingConfig?: ThinkingConfig;
    toolConfig?: ToolConfig;
    tools?: ToolListUnion;
    topK?: number;
    topP?: number;
}
```

----------------------------------------

TITLE: Browser Initialization with API Key
DESCRIPTION: Example of initializing the Google Gen AI SDK in a browser environment. Note that this approach should be used cautiously as it exposes API keys in client-side code.
SOURCE: https://github.com/googleapis/js-genai/blob/main/README.md#2025-04-23_snippet_3

LANGUAGE: typescript
CODE:
```
import { GoogleGenAI } from '@google/genai';
const ai = new GoogleGenAI({apiKey: 'GEMINI_API_KEY'});
```

----------------------------------------

TITLE: Implementing Live Class in TypeScript
DESCRIPTION: The Live class provides functionality for connecting to live sessions. It includes a constructor and a connect method that returns a Promise resolving to a Session object.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_43

LANGUAGE: TypeScript
CODE:
```
// @public
export class Live {
    // Warning: (ae-forgotten-export) The symbol "Auth" needs to be exported by the entry point index.d.ts
    // Warning: (ae-forgotten-export) The symbol "WebSocketFactory" needs to be exported by the entry point index.d.ts
    constructor(apiClient: ApiClient, auth: Auth, webSocketFactory: WebSocketFactory);
    connect(params: types.LiveConnectParameters): Promise<Session>;
}
```

----------------------------------------

TITLE: Defining Model Interface in TypeScript
DESCRIPTION: Defines an interface for models, including properties like description, display name, endpoints, token limits, and supported actions.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_60

LANGUAGE: TypeScript
CODE:
```
// @public
export interface Model {
    description?: string;
    displayName?: string;
    endpoints?: Endpoint[];
    inputTokenLimit?: number;
    labels?: Record<string, string>;
    name?: string;
    outputTokenLimit?: number;
    supportedActions?: string[];
    tunedModelInfo?: TunedModelInfo;
    version?: string;
}
```

----------------------------------------

TITLE: Defining GenerateContentConfig Interface in TypeScript
DESCRIPTION: Specifies an interface for content generation configuration, including various optional properties for controlling the generation process.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_19

LANGUAGE: typescript
CODE:
```
export interface GenerateContentConfig {
    abortSignal?: AbortSignal;
    audioTimestamp?: boolean;
    cachedContent?: string;
    candidateCount?: number;
    frequencyPenalty?: number;
    httpOptions?: HttpOptions;
    labels?: Record<string, string>;
    logprobs?: number;
    maxOutputTokens?: number;
    mediaResolution?: MediaResolution;
    modelSelectionConfig?: ModelSelectionConfig;
    presencePenalty?: number;
    responseLogprobs?: boolean;
    responseMimeType?: string;
    responseModalities?: string[];
    responseSchema?: SchemaUnion;
    routingConfig?: GenerationConfigRoutingConfig;
    safetySettings?: SafetySetting[];
    seed?: number;
    speechConfig?: SpeechConfigUnion;
    stopSequences?: string[];
    systemInstruction?: ContentUnion;
    temperature?: number;
    thinkingConfig?: ThinkingConfig;
    toolConfig?: ToolConfig;
    tools?: ToolListUnion;
    topK?: number;
    topP?: number;
}
```

----------------------------------------

TITLE: Defining SafetyRating Interface in TypeScript
DESCRIPTION: Defines an interface for safety ratings, including properties for blocked status, harm category, probability, and severity.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_88

LANGUAGE: TypeScript
CODE:
```
export interface SafetyRating {
    blocked?: boolean;
    category?: HarmCategory;
    probability?: HarmProbability;
    probabilityScore?: number;
    severity?: HarmSeverity;
    severityScore?: number;
}
```

----------------------------------------

TITLE: Defining Session Class in TypeScript
DESCRIPTION: Implements a Session class for managing WebSocket connections and sending various types of content and inputs.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_54

LANGUAGE: TypeScript
CODE:
```
export class Session {
    constructor(conn: WebSocket_2, apiClient: ApiClient);
    close(): void;
    readonly conn: WebSocket_2;
    sendClientContent(params: types.LiveSendClientContentParameters): void;
    sendRealtimeInput(params: types.LiveSendRealtimeInputParameters): void;
    sendToolResponse(params: types.LiveSendToolResponseParameters): void;
}
```

----------------------------------------

TITLE: Defining Part Interface in TypeScript
DESCRIPTION: Defines an interface for content parts, including various types of data such as code execution results, file data, and function calls.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_31

LANGUAGE: TypeScript
CODE:
```
// @public
export interface Part {
    codeExecutionResult?: CodeExecutionResult;
    executableCode?: ExecutableCode;
    fileData?: FileData;
    functionCall?: FunctionCall;
    functionResponse?: FunctionResponse;
    inlineData?: Blob_2;
    text?: string;
    thought?: boolean;
    videoMetadata?: VideoMetadata;
}
```

----------------------------------------

TITLE: Defining Safety Setting Interface in TypeScript
DESCRIPTION: TypeScript interface for configuring safety settings when making requests to the AI model. It allows specifying harm categories, blocking methods, and threshold levels.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_48

LANGUAGE: typescript
CODE:
```
// @public
export interface SafetySetting {
    category?: HarmCategory;
    method?: HarmBlockMethod;
    threshold?: HarmBlockThreshold;
}
```

----------------------------------------

TITLE: Defining SafetySetting Interface in TypeScript
DESCRIPTION: Specifies an interface for safety settings, including harm category, blocking method, and threshold.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_89

LANGUAGE: TypeScript
CODE:
```
export interface SafetySetting {
    category?: HarmCategory;
    method?: HarmBlockMethod;
    threshold?: HarmBlockThreshold;
}
```

----------------------------------------

TITLE: Implementing Session Class for WebSocket Communication in TypeScript
DESCRIPTION: TypeScript class that manages WebSocket connections for real-time AI interactions. It provides methods for sending content, real-time input, and tool responses to the AI service.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_50

LANGUAGE: typescript
CODE:
```
// @public
export class Session {
    constructor(conn: WebSocket_2, apiClient: ApiClient);
    close(): void;
    // Warning: (ae-forgotten-export) The symbol "WebSocket_2" needs to be exported by the entry point index.d.ts
    //
    // (undocumented)
    readonly conn: WebSocket_2;
    sendClientContent(params: types.LiveSendClientContentParameters): void;
    sendRealtimeInput(params: types.LiveSendRealtimeInputParameters): void;
    sendToolResponse(params: types.LiveSendToolResponseParameters): void;
}
```

----------------------------------------

TITLE: Defining GenerationConfig Interface in TypeScript
DESCRIPTION: Interface for configuring text generation parameters such as temperature, token limits, and stopping conditions.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_33

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerationConfig {
    audioTimestamp?: boolean;
    candidateCount?: number;
    frequencyPenalty?: number;
    logprobs?: number;
    maxOutputTokens?: number;
    mediaResolution?: MediaResolution;
    presencePenalty?: number;
    responseLogprobs?: boolean;
    responseMimeType?: string;
    responseSchema?: Schema;
    routingConfig?: GenerationConfigRoutingConfig;
    seed?: number;
    stopSequences?: string[];
    temperature?: number;
    topK?: number;
    topP?: number;
}
```

----------------------------------------

TITLE: Defining Tool Interface in TypeScript
DESCRIPTION: Specifies an interface for various tool types, including code execution, function declarations, and search capabilities.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_92

LANGUAGE: TypeScript
CODE:
```
export interface Tool {
    codeExecution?: ToolCodeExecution;
    functionDeclarations?: FunctionDeclaration[];
    googleSearch?: GoogleSearch;
    googleSearchRetrieval?: GoogleSearchRetrieval;
    retrieval?: Retrieval;
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfig Interface in TypeScript
DESCRIPTION: Defines an interface for RAG (Retrieval-Augmented Generation) retrieval configuration, including filter, hybrid search, ranking, and top-K settings.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_72

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfig {
    filter?: RagRetrievalConfigFilter;
    hybridSearch?: RagRetrievalConfigHybridSearch;
    ranking?: RagRetrievalConfigRanking;
    topK?: number;
}
```

----------------------------------------

TITLE: Implementing GenerateImagesResponse Class in TypeScript
DESCRIPTION: Class representing a response from image generation with arrays of generated images and safety attributes.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_28

LANGUAGE: typescript
CODE:
```
// @public
export class GenerateImagesResponse {
    generatedImages?: GeneratedImage[];
    positivePromptSafetyAttributes?: SafetyAttributes;
}
```

----------------------------------------

TITLE: Defining Enums for Harm Categories and Severities in TypeScript
DESCRIPTION: Enumerates various harm categories, probabilities, severities, and block thresholds used in content moderation and safety features of the API.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_43

LANGUAGE: TypeScript
CODE:
```
// @public
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

// @public
export enum HarmProbability {
    // (undocumented)
    HARM_PROBABILITY_UNSPECIFIED = "HARM_PROBABILITY_UNSPECIFIED",
    // (undocumented)
    HIGH = "HIGH",
    // (undocumented)
    LOW = "LOW",
    // (undocumented)
    MEDIUM = "MEDIUM",
    // (undocumented)
    NEGLIGIBLE = "NEGLIGIBLE"
}

// @public
export enum HarmSeverity {
    // (undocumented)
    HARM_SEVERITY_HIGH = "HARM_SEVERITY_HIGH",
    // (undocumented)
    HARM_SEVERITY_LOW = "HARM_SEVERITY_LOW",
    // (undocumented)
    HARM_SEVERITY_MEDIUM = "HARM_SEVERITY_MEDIUM",
    // (undocumented)
    HARM_SEVERITY_NEGLIGIBLE = "HARM_SEVERITY_NEGLIGIBLE",
    // (undocumented)
    HARM_SEVERITY_UNSPECIFIED = "HARM_SEVERITY_UNSPECIFIED"
}

// @public
export enum HarmBlockThreshold {
    // (undocumented)
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE",
    // (undocumented)
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE",
    // (undocumented)
    BLOCK_NONE = "BLOCK_NONE",
    // (undocumented)
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH",
    // (undocumented)
    HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
    // (undocumented)
    OFF = "OFF"
}
```

----------------------------------------

TITLE: Defining GenerateVideosParameters Interface in TypeScript
DESCRIPTION: Interface for parameters required to generate videos, including the model, optional prompt, image, and configuration.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_31

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateVideosParameters {
    config?: GenerateVideosConfig;
    image?: Image_2;
    model: string;
    prompt?: string;
}
```

----------------------------------------

TITLE: Defining GenerateImagesConfig Interface in TypeScript
DESCRIPTION: Interface for configuring image generation with parameters such as aspect ratio, prompt enhancement, and safety filters.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_26

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateImagesConfig {
    abortSignal?: AbortSignal;
    addWatermark?: boolean;
    aspectRatio?: string;
    enhancePrompt?: boolean;
    guidanceScale?: number;
    httpOptions?: HttpOptions;
    includeRaiReason?: boolean;
    includeSafetyAttributes?: boolean;
    language?: ImagePromptLanguage;
    negativePrompt?: string;
    numberOfImages?: number;
    outputCompressionQuality?: number;
    outputGcsUri?: string;
    outputMimeType?: string;
    personGeneration?: PersonGeneration;
    safetyFilterLevel?: SafetyFilterLevel;
    seed?: number;
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfig Interface in TypeScript
DESCRIPTION: Defines an interface for RAG (Retrieval-Augmented Generation) retrieval configuration, including filter, hybrid search, ranking, and top-K settings.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_35

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfig {
    filter?: RagRetrievalConfigFilter;
    hybridSearch?: RagRetrievalConfigHybridSearch;
    ranking?: RagRetrievalConfigRanking;
    topK?: number;
}
```

----------------------------------------

TITLE: Defining GenerateContentParameters Interface in TypeScript
DESCRIPTION: Specifies an interface for content generation parameters, including properties for configuration, contents, and model.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_20

LANGUAGE: typescript
CODE:
```
export interface GenerateContentParameters {
    config?: GenerateContentConfig;
    contents: ContentListUnion;
    model: string;
}
```

----------------------------------------

TITLE: Defining GenerationConfig Interface in TypeScript
DESCRIPTION: Specifies an interface for generation configuration, including various optional properties for controlling the generation process.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_33

LANGUAGE: typescript
CODE:
```
export interface GenerationConfig {
    audioTimestamp?: boolean;
    candidateCount?: number;
    frequencyPenalty?: number;
    logprobs?: number;
    maxOutputTokens?: number;
    mediaResolution?: MediaResolution;
    presencePenalty?: number;
    responseLogprobs?: boolean;
    responseMimeType?: string;
    responseSchema?: Schema;
    routingConfig?: GenerationConfigRoutingConfig;
    seed?: number;
    stopSequences?: string[];
    temperature?: number;
    topK?: number;
    topP?: number;
}
```

----------------------------------------

TITLE: Defining FunctionDeclaration Interface in TypeScript
DESCRIPTION: Specifies an interface for function declarations, including optional properties for description, name, parameters, and response schema.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_17

LANGUAGE: typescript
CODE:
```
export interface FunctionDeclaration {
    description?: string;
    name?: string;
    parameters?: Schema;
    response?: Schema;
}
```

----------------------------------------

TITLE: Defining GenerateContentParameters Interface in TypeScript
DESCRIPTION: Interface for parameters required to generate content, including the model name, contents to process, and optional configuration.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_20

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateContentParameters {
    config?: GenerateContentConfig;
    contents: ContentListUnion;
    model: string;
}
```

----------------------------------------

TITLE: Implementing GenerateImagesResponse Class in TypeScript
DESCRIPTION: Defines a class for image generation responses, including properties for generated images and positive prompt safety attributes.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_28

LANGUAGE: typescript
CODE:
```
export class GenerateImagesResponse {
    generatedImages?: GeneratedImage[];
    positivePromptSafetyAttributes?: SafetyAttributes;
}
```

----------------------------------------

TITLE: Defining Tool Interface in TypeScript
DESCRIPTION: Specifies the Tool interface with various optional properties for different types of tools and functionalities.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_56

LANGUAGE: TypeScript
CODE:
```
export interface Tool {
    codeExecution?: ToolCodeExecution;
    functionDeclarations?: FunctionDeclaration[];
    googleSearch?: GoogleSearch;
    googleSearchRetrieval?: GoogleSearchRetrieval;
    retrieval?: Retrieval;
}
```

----------------------------------------

TITLE: Defining FunctionCallingConfig Interface in TypeScript
DESCRIPTION: Specifies an interface for function calling configuration, including optional properties for allowed function names and mode.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_15

LANGUAGE: typescript
CODE:
```
export interface FunctionCallingConfig {
    allowedFunctionNames?: string[];
    mode?: FunctionCallingConfigMode;
}
```

----------------------------------------

TITLE: Defining FunctionCall Interface in TypeScript
DESCRIPTION: Specifies an interface for function calls, including optional properties for arguments, ID, and name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_14

LANGUAGE: typescript
CODE:
```
export interface FunctionCall {
    args?: Record<string, unknown>;
    id?: string;
    name?: string;
}
```

----------------------------------------

TITLE: Defining GenerateVideosParameters Interface in TypeScript
DESCRIPTION: Specifies an interface for video generation parameters, including properties for configuration, image, model, and prompt.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_31

LANGUAGE: typescript
CODE:
```
export interface GenerateVideosParameters {
    config?: GenerateVideosConfig;
    image?: Image_2;
    model: string;
    prompt?: string;
}
```

----------------------------------------

TITLE: Defining GenerateImagesParameters Interface in TypeScript
DESCRIPTION: Interface for parameters required to generate images, including the model, prompt, and optional configuration.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_27

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateImagesParameters {
    config?: GenerateImagesConfig;
    model: string;
    prompt: string;
}
```

----------------------------------------

TITLE: Installing and Running GenAI TypeScript Web Sample
DESCRIPTION: Commands to install dependencies and start the development server for the GenAI TypeScript web sample application
SOURCE: https://github.com/googleapis/js-genai/blob/main/sdk-samples/web/README.md#2025-04-23_snippet_0

LANGUAGE: bash
CODE:
```
npm install
npm run dev
```

----------------------------------------

TITLE: Implementing FunctionResponse Class in TypeScript
DESCRIPTION: Class representing a response from a function call with ID, name, and response data properties.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_18

LANGUAGE: typescript
CODE:
```
// @public
export class FunctionResponse {
    id?: string;
    name?: string;
    response?: Record<string, unknown>;
}
```

----------------------------------------

TITLE: Defining GenerateImagesConfig Interface in TypeScript
DESCRIPTION: Specifies an interface for image generation configuration, including various optional properties for controlling the generation process.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_26

LANGUAGE: typescript
CODE:
```
export interface GenerateImagesConfig {
    abortSignal?: AbortSignal;
    addWatermark?: boolean;
    aspectRatio?: string;
    enhancePrompt?: boolean;
    guidanceScale?: number;
    httpOptions?: HttpOptions;
    includeRaiReason?: boolean;
    includeSafetyAttributes?: boolean;
    language?: ImagePromptLanguage;
    negativePrompt?: string;
    numberOfImages?: number;
    outputCompressionQuality?: number;
    outputGcsUri?: string;
    outputMimeType?: string;
    personGeneration?: PersonGeneration;
    safetyFilterLevel?: SafetyFilterLevel;
    seed?: number;
}
```

----------------------------------------

TITLE: Implementing Files Class in TypeScript
DESCRIPTION: Defines a Files class extending BaseModule, providing methods for file operations such as delete, get, list, and upload.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_9

LANGUAGE: typescript
CODE:
```
export class Files extends BaseModule {
    constructor(apiClient: ApiClient);
    delete(params: types.DeleteFileParameters): Promise<types.DeleteFileResponse>;
    get(params: types.GetFileParameters): Promise<types.File>;
    list: (params?: types.ListFilesParameters) => Promise<Pager<types.File>>;
    upload(params: types.UploadFileParameters): Promise<types.File>;
}
```

----------------------------------------

TITLE: Defining SafetySetting Interface in TypeScript
DESCRIPTION: Specifies the SafetySetting interface with optional properties for harm category, blocking method, and threshold.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_52

LANGUAGE: TypeScript
CODE:
```
export interface SafetySetting {
    category?: HarmCategory;
    method?: HarmBlockMethod;
    threshold?: HarmBlockThreshold;
}
```

----------------------------------------

TITLE: Defining GenerateVideosConfig Interface in TypeScript
DESCRIPTION: Specifies an interface for video generation configuration, including various optional properties for controlling the generation process.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_29

LANGUAGE: typescript
CODE:
```
export interface GenerateVideosConfig {
    abortSignal?: AbortSignal;
    aspectRatio?: string;
    durationSeconds?: number;
    enhancePrompt?: boolean;
    fps?: number;
    httpOptions?: HttpOptions;
    negativePrompt?: string;
    numberOfVideos?: number;
    outputGcsUri?: string;
    personGeneration?: string;
    pubsubTopic?: string;
    resolution?: string;
    seed?: number;
}
```

----------------------------------------

TITLE: Defining FunctionCall Interface in TypeScript
DESCRIPTION: Interface for function calls made by the model, including function arguments, ID, and name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_14

LANGUAGE: typescript
CODE:
```
// @public
export interface FunctionCall {
    args?: Record<string, unknown>;
    id?: string;
    name?: string;
}
```

----------------------------------------

TITLE: Defining SafetyFilterLevel Enum in TypeScript
DESCRIPTION: Defines an enum for safety filter levels, including options to block content based on severity levels.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_87

LANGUAGE: TypeScript
CODE:
```
// @public
export enum SafetyFilterLevel {
    // (undocumented)
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE",
    // (undocumented)
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE",
    // (undocumented)
    BLOCK_NONE = "BLOCK_NONE",
    // (undocumented)
}
```

----------------------------------------

TITLE: Defining Retrieval Interface in TypeScript
DESCRIPTION: Defines an interface for retrieval settings, including options for disabling attribution and specifying Vertex AI Search or RAG store.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_84

LANGUAGE: TypeScript
CODE:
```
// @public
export interface Retrieval {
    disableAttribution?: boolean;
    vertexAiSearch?: VertexAISearch;
    vertexRagStore?: VertexRagStore;
}
```

----------------------------------------

TITLE: Defining FunctionCallingConfig Interface in TypeScript
DESCRIPTION: Interface for configuring function calling behavior with optional allowed function names and mode settings.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_15

LANGUAGE: typescript
CODE:
```
// @public
export interface FunctionCallingConfig {
    allowedFunctionNames?: string[];
    mode?: FunctionCallingConfigMode;
}
```

----------------------------------------

TITLE: Implementing GenerateVideosResponse Class in TypeScript
DESCRIPTION: Class representing a response from video generation with generated videos and content filtering information.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_32

LANGUAGE: typescript
CODE:
```
// @public
export class GenerateVideosResponse {
    generatedVideos?: GeneratedVideo[];
    raiMediaFilteredCount?: number;
    raiMediaFilteredReasons?: string[];
}
```

----------------------------------------

TITLE: Implementing GenerateContentResponseUsageMetadata Class in TypeScript
DESCRIPTION: Defines a class for usage metadata in content generation responses, including various token counts and traffic type.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_23

LANGUAGE: typescript
CODE:
```
export class GenerateContentResponseUsageMetadata {
    cachedContentTokenCount?: number;
    cacheTokensDetails?: ModalityTokenCount[];
    candidatesTokenCount?: number;
    candidatesTokensDetails?: ModalityTokenCount[];
    promptTokenCount?: number;
    promptTokensDetails?: ModalityTokenCount[];
    thoughtsTokenCount?: number;
    toolUsePromptTokenCount?: number;
    toolUsePromptTokensDetails?: ModalityTokenCount[];
    totalTokenCount?: number;
    trafficType?: TrafficType;
}
```

----------------------------------------

TITLE: Defining RealtimeInputConfig Interface in TypeScript
DESCRIPTION: Defines an interface for realtime input configuration, including activity handling, automatic activity detection, and turn coverage settings.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_79

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RealtimeInputConfig {
    activityHandling?: ActivityHandling;
    automaticActivityDetection?: AutomaticActivityDetection;
    turnCoverage?: TurnCoverage;
}
```

----------------------------------------

TITLE: Interface Definition - File Handling Types
DESCRIPTION: Interfaces and enums for handling file operations including metadata, states and sources
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_2

LANGUAGE: typescript
CODE:
```
interface File_2 {
    createTime?: string;
    displayName?: string;
    downloadUri?: string;
    error?: FileStatus;
    expirationTime?: string;
    mimeType?: string;
    name?: string;
    sha256Hash?: string;
    sizeBytes?: string;
    source?: FileSource;
    state?: FileState;
    updateTime?: string;
    uri?: string;
    videoMetadata?: Record<string, unknown>;
}

export enum FileSource {
    GENERATED = "GENERATED",
    SOURCE_UNSPECIFIED = "SOURCE_UNSPECIFIED",
    UPLOADED = "UPLOADED"
}

export enum FileState {
    ACTIVE = "ACTIVE",
    FAILED = "FAILED",
    PROCESSING = "PROCESSING",
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Declaring FunctionCallingConfigMode Enum in TypeScript
DESCRIPTION: Defines an enum for function calling configuration modes, including options for any, auto, none, and unspecified.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_16

LANGUAGE: typescript
CODE:
```
export enum FunctionCallingConfigMode {
    ANY = "ANY",
    AUTO = "AUTO",
    MODE_UNSPECIFIED = "MODE_UNSPECIFIED",
    NONE = "NONE"
}
```

----------------------------------------

TITLE: Defining GenerateVideosOperation Interface in TypeScript
DESCRIPTION: Interface representing a long-running video generation operation with status, metadata, and response properties.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_30

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateVideosOperation {
    done?: boolean;
    error?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
    name?: string;
    response?: GenerateVideosResponse;
}
```

----------------------------------------

TITLE: Defining File Interface in TypeScript
DESCRIPTION: Interface representing a file in the GenAI API with various metadata properties such as timestamps, file state, and URIs.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_7

LANGUAGE: typescript
CODE:
```
// @public
interface File_2 {
    createTime?: string;
    displayName?: string;
    downloadUri?: string;
    error?: FileStatus;
    expirationTime?: string;
    mimeType?: string;
    name?: string;
    sha256Hash?: string;
    sizeBytes?: string;
    source?: FileSource;
    state?: FileState;
    updateTime?: string;
    uri?: string;
    videoMetadata?: Record<string, unknown>;
}
export { File_2 as File }
```

----------------------------------------

TITLE: Implementing GenerateContentResponseUsageMetadata Class in TypeScript
DESCRIPTION: Class containing token usage metadata for the content generation, including counts for prompt, candidates, and total tokens used.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_23

LANGUAGE: typescript
CODE:
```
// @public
export class GenerateContentResponseUsageMetadata {
    cachedContentTokenCount?: number;
    cacheTokensDetails?: ModalityTokenCount[];
    candidatesTokenCount?: number;
    candidatesTokensDetails?: ModalityTokenCount[];
    promptTokenCount?: number;
    promptTokensDetails?: ModalityTokenCount[];
    thoughtsTokenCount?: number;
    toolUsePromptTokenCount?: number;
    toolUsePromptTokensDetails?: ModalityTokenCount[];
    totalTokenCount?: number;
    trafficType?: TrafficType;
}
```

----------------------------------------

TITLE: Defining Retrieval Interface in TypeScript
DESCRIPTION: Defines an interface for retrieval configuration, including options for disabling attribution and specifying Vertex AI search or RAG store.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_47

LANGUAGE: TypeScript
CODE:
```
// @public
export interface Retrieval {
    disableAttribution?: boolean;
    vertexAiSearch?: VertexAISearch;
    vertexRagStore?: VertexRagStore;
}
```

----------------------------------------

TITLE: Implementing GenerateVideosResponse Class in TypeScript
DESCRIPTION: Defines a class for video generation responses, including properties for generated videos and RAI media filtering information.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_32

LANGUAGE: typescript
CODE:
```
export class GenerateVideosResponse {
    generatedVideos?: GeneratedVideo[];
    raiMediaFilteredCount?: number;
    raiMediaFilteredReasons?: string[];
}
```

----------------------------------------

TITLE: Defining FileData Interface in TypeScript
DESCRIPTION: Specifies an interface for file data, including optional properties for file URI and MIME type.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_8

LANGUAGE: typescript
CODE:
```
export interface FileData {
    fileUri?: string;
    mimeType?: string;
}
```

----------------------------------------

TITLE: Implementing GenerateContentResponsePromptFeedback Class in TypeScript
DESCRIPTION: Class containing feedback information about prompt processing, including safety ratings and block reasons.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_22

LANGUAGE: typescript
CODE:
```
// @public
export class GenerateContentResponsePromptFeedback {
    blockReason?: BlockedReason;
    blockReasonMessage?: string;
    safetyRatings?: SafetyRating[];
}
```

----------------------------------------

TITLE: Defining GenerateVideosConfig Interface in TypeScript
DESCRIPTION: Interface for configuring video generation with parameters such as duration, FPS, resolution, and seed value.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_29

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerateVideosConfig {
    abortSignal?: AbortSignal;
    aspectRatio?: string;
    durationSeconds?: number;
    enhancePrompt?: boolean;
    fps?: number;
    httpOptions?: HttpOptions;
    negativePrompt?: string;
    numberOfVideos?: number;
    outputGcsUri?: string;
    personGeneration?: string;
    pubsubTopic?: string;
    resolution?: string;
    seed?: number;
}
```

----------------------------------------

TITLE: Defining Pager Class in TypeScript
DESCRIPTION: Defines a generic class for paging through items, with methods for iteration, checking for next pages, and retrieving items.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_67

LANGUAGE: TypeScript
CODE:
```
// @public
export class Pager<T> implements AsyncIterable<T> {
    [Symbol.asyncIterator](): AsyncIterator<T>;
    constructor(name: PagedItem, request: (params: PagedItemConfig) => Promise<PagedItemResponse<T>>, response: PagedItemResponse<T>, params: PagedItemConfig);
    getItem(index: number): T;
    hasNextPage(): boolean;
    // (undocumented)
    protected idxInternal: number;
    get name(): PagedItem;
    nextPage(): Promise<T[]>;
    get page(): T[];
    get pageLength(): number;
    get pageSize(): number;
    get params(): PagedItemConfig;
    // Warning: (ae-forgotten-export) The symbol "PagedItemConfig" needs to be exported by the entry point index.d.ts
    // Warning: (ae-forgotten-export) The symbol "PagedItemResponse" needs to be exported by the entry point index.d.ts
    //
    // (undocumented)
    protected requestInternal: (params: PagedItemConfig) => Promise<PagedItemResponse<T>>;
}
```

----------------------------------------

TITLE: Defining Schema Interface in TypeScript
DESCRIPTION: Creates a comprehensive Schema interface with various optional properties for defining data structures and validation rules.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_53

LANGUAGE: TypeScript
CODE:
```
export interface Schema {
    anyOf?: Schema[];
    default?: unknown;
    description?: string;
    enum?: string[];
    example?: unknown;
    format?: string;
    items?: Schema;
    maximum?: number;
    maxItems?: string;
    maxLength?: string;
    maxProperties?: string;
    minimum?: number;
    minItems?: string;
    minLength?: string;
    minProperties?: string;
    nullable?: boolean;
    pattern?: string;
    properties?: Record<string, Schema>;
    propertyOrdering?: string[];
    required?: string[];
    title?: string;
    type?: Type;
}
```

----------------------------------------

TITLE: Defining GeneratedImage Interface in TypeScript
DESCRIPTION: Interface representing a generated image with the image data, enhanced prompt, and safety attributes.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_24

LANGUAGE: typescript
CODE:
```
// @public
export interface GeneratedImage {
    enhancedPrompt?: string;
    image?: Image_2;
    raiFilteredReason?: string;
    safetyAttributes?: SafetyAttributes;
}
```

----------------------------------------

TITLE: Declaring FinishReason Enum in TypeScript
DESCRIPTION: Defines an enum for finish reasons in AI model responses, including various completion and error scenarios.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_13

LANGUAGE: typescript
CODE:
```
export enum FinishReason {
    BLOCKLIST = "BLOCKLIST",
    FINISH_REASON_UNSPECIFIED = "FINISH_REASON_UNSPECIFIED",
    IMAGE_SAFETY = "IMAGE_SAFETY",
    MALFORMED_FUNCTION_CALL = "MALFORMED_FUNCTION_CALL",
    MAX_TOKENS = "MAX_TOKENS",
    OTHER = "OTHER",
    PROHIBITED_CONTENT = "PROHIBITED_CONTENT",
    RECITATION = "RECITATION",
    SAFETY = "SAFETY",
    SPII = "SPII",
    STOP = "STOP"
}
```

----------------------------------------

TITLE: Defining Endpoint Interface in TypeScript
DESCRIPTION: Defines an interface for an AI model endpoint, including optional properties for deployed model ID and name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_1

LANGUAGE: typescript
CODE:
```
export interface Endpoint {
    deployedModelId?: string;
    name?: string;
}
```

----------------------------------------

TITLE: Defining Schema Interface for API Parameters in TypeScript
DESCRIPTION: TypeScript interface for schema definitions used in API parameter validation. It supports JSON Schema-like validation with properties for type constraints, descriptions, and format validations.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_49

LANGUAGE: typescript
CODE:
```
// @public
export interface Schema {
    anyOf?: Schema[];
    default?: unknown;
    description?: string;
    enum?: string[];
    example?: unknown;
    format?: string;
    items?: Schema;
    maximum?: number;
    maxItems?: string;
    maxLength?: string;
    maxProperties?: string;
    minimum?: number;
    minItems?: string;
    minLength?: string;
    minProperties?: string;
    nullable?: boolean;
    pattern?: string;
    properties?: Record<string, Schema>;
    propertyOrdering?: string[];
    required?: string[];
    title?: string;
    type?: Type;
}
```

----------------------------------------

TITLE: Defining GeneratedImage Interface in TypeScript
DESCRIPTION: Specifies an interface for generated image data, including properties for enhanced prompt, image, RAI filtered reason, and safety attributes.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_24

LANGUAGE: typescript
CODE:
```
export interface GeneratedImage {
    enhancedPrompt?: string;
    image?: Image_2;
    raiFilteredReason?: string;
    safetyAttributes?: SafetyAttributes;
}
```

----------------------------------------

TITLE: Interface Definition - Endpoint and Enums
DESCRIPTION: Core type definitions for endpoint configuration and sensitivity settings used in the API
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_1

LANGUAGE: typescript
CODE:
```
export interface Endpoint {
    deployedModelId?: string;
    name?: string;
}

export enum EndSensitivity {
    END_SENSITIVITY_HIGH = "END_SENSITIVITY_HIGH",
    END_SENSITIVITY_LOW = "END_SENSITIVITY_LOW",
    END_SENSITIVITY_UNSPECIFIED = "END_SENSITIVITY_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Defining SafetyRating Interface in TypeScript
DESCRIPTION: Defines the SafetyRating interface with optional properties for blocked status, harm category, probability, and severity scores.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_51

LANGUAGE: TypeScript
CODE:
```
export interface SafetyRating {
    blocked?: boolean;
    category?: HarmCategory;
    probability?: HarmProbability;
    probabilityScore?: number;
    severity?: HarmSeverity;
    severityScore?: number;
}
```

----------------------------------------

TITLE: Defining GeneratedVideo Interface in TypeScript
DESCRIPTION: Specifies an interface for generated video data, including an optional video property.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_25

LANGUAGE: typescript
CODE:
```
export interface GeneratedVideo {
    video?: Video;
}
```

----------------------------------------

TITLE: Defining SafetyAttributes Interface in TypeScript
DESCRIPTION: Defines an interface for safety attributes, including categories, content type, and scores.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_86

LANGUAGE: TypeScript
CODE:
```
// @public
export interface SafetyAttributes {
    categories?: string[];
    contentType?: string;
    scores?: number[];
}
```

----------------------------------------

TITLE: Defining GetCachedContentParameters Interface in TypeScript
DESCRIPTION: Interface for parameters required to retrieve cached content, including the content name and optional configuration.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_38

LANGUAGE: typescript
CODE:
```
// @public
export interface GetCachedContentParameters {
    config?: GetCachedContentConfig;
    name: string;
}
```

----------------------------------------

TITLE: Defining SafetyAttributes Interface in TypeScript
DESCRIPTION: Defines an interface for safety attributes, including categories, content type, and scores.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_49

LANGUAGE: TypeScript
CODE:
```
// @public
export interface SafetyAttributes {
    categories?: string[];
    contentType?: string;
    scores?: number[];
}
```

----------------------------------------

TITLE: Defining Schema Interface in TypeScript
DESCRIPTION: Creates a comprehensive interface for schema definitions, including various properties for type validation and structure.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_90

LANGUAGE: TypeScript
CODE:
```
export interface Schema {
    anyOf?: Schema[];
    default?: unknown;
    description?: string;
    enum?: string[];
    example?: unknown;
    format?: string;
    items?: Schema;
    maximum?: number;
    maxItems?: string;
    maxLength?: string;
    maxProperties?: string;
    minimum?: number;
    minItems?: string;
    minLength?: string;
    minProperties?: string;
    nullable?: boolean;
    pattern?: string;
    properties?: Record<string, Schema>;
    propertyOrdering?: string[];
    required?: string[];
    title?: string;
    type?: Type;
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfigRankingRankService Interface in TypeScript
DESCRIPTION: Defines an interface for RAG retrieval configuration ranking service, including the model name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_77

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfigRankingRankService {
    modelName?: string;
}
```

----------------------------------------

TITLE: Defining GetCachedContentParameters Interface in TypeScript
DESCRIPTION: Specifies an interface for cached content retrieval parameters, including properties for configuration and name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_38

LANGUAGE: typescript
CODE:
```
export interface GetCachedContentParameters {
    config?: GetCachedContentConfig;
    name: string;
}
```

----------------------------------------

TITLE: HarmCategory Enum Definition
DESCRIPTION: Enumeration defining different categories of harmful content that can be detected and filtered by the API.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_6

LANGUAGE: typescript
CODE:
```
export enum HarmCategory {
    HARM_CATEGORY_CIVIC_INTEGRITY = "HARM_CATEGORY_CIVIC_INTEGRITY",
    HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT",
    HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT",
    HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH",
    HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    HARM_CATEGORY_UNSPECIFIED = "HARM_CATEGORY_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfigFilter Interface in TypeScript
DESCRIPTION: Defines an interface for RAG retrieval configuration filters, including metadata filter and vector distance/similarity thresholds.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_73

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfigFilter {
    metadataFilter?: string;
    vectorDistanceThreshold?: number;
    vectorSimilarityThreshold?: number;
}
```

----------------------------------------

TITLE: Defining GenerateVideosOperation Interface in TypeScript
DESCRIPTION: Specifies an interface for video generation operations, including properties for operation status, metadata, and response.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_30

LANGUAGE: typescript
CODE:
```
export interface GenerateVideosOperation {
    done?: boolean;
    error?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
    name?: string;
    response?: GenerateVideosResponse;
}
```

----------------------------------------

TITLE: Defining GetFileParameters Interface in TypeScript
DESCRIPTION: This snippet defines the GetFileParameters interface used for retrieving file information. It includes an optional config property and a required name property.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_40

LANGUAGE: TypeScript
CODE:
```
// @public
export interface GetFileParameters {
    config?: GetFileConfig;
    name: string;
}
```

----------------------------------------

TITLE: Defining GenerationConfigRoutingConfig Interface in TypeScript
DESCRIPTION: Specifies an interface for generation config routing configuration, including optional properties for auto and manual routing modes.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_34

LANGUAGE: typescript
CODE:
```
export interface GenerationConfigRoutingConfig {
    autoMode?: GenerationConfigRoutingConfigAutoRoutingMode;
    manualMode?: GenerationConfigRoutingConfigManualRoutingMode;
}
```

----------------------------------------

TITLE: Defining ModelSelectionConfig Interface in TypeScript
DESCRIPTION: Defines an interface for model selection configuration, including feature selection preference.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_62

LANGUAGE: TypeScript
CODE:
```
// @public
export interface ModelSelectionConfig {
    featureSelectionPreference?: FeatureSelectionPreference;
}
```

----------------------------------------

TITLE: Defining FetchPredictOperationParameters Interface in TypeScript
DESCRIPTION: Interface for parameters required to fetch a prediction operation, including operation name, resource name, and optional config.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_6

LANGUAGE: typescript
CODE:
```
// @public
export interface FetchPredictOperationParameters {
    config?: FetchPredictOperationConfig;
    operationName: string;
    // (undocumented)
    resourceName: string;
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfigRankingLlmRanker Interface in TypeScript
DESCRIPTION: Defines an interface for RAG retrieval configuration ranking LLM ranker, including the model name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_76

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfigRankingLlmRanker {
    modelName?: string;
}
```

----------------------------------------

TITLE: Defining ModelSelectionConfig Interface in TypeScript
DESCRIPTION: Defines an interface for model selection configuration, including feature selection preference.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_25

LANGUAGE: TypeScript
CODE:
```
// @public
export interface ModelSelectionConfig {
    featureSelectionPreference?: FeatureSelectionPreference;
}
```

----------------------------------------

TITLE: Implementing FunctionResponse Class in TypeScript
DESCRIPTION: Defines a FunctionResponse class with optional properties for ID, name, and response data.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_18

LANGUAGE: typescript
CODE:
```
export class FunctionResponse {
    id?: string;
    name?: string;
    response?: Record<string, unknown>;
}
```

----------------------------------------

TITLE: Defining FetchPredictOperationConfig Interface in TypeScript
DESCRIPTION: Interface for configuring predict operation fetches with optional abort signal and HTTP options.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_5

LANGUAGE: typescript
CODE:
```
// @public (undocumented)
export interface FetchPredictOperationConfig {
    abortSignal?: AbortSignal;
    httpOptions?: HttpOptions;
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfigRankingLlmRanker Interface in TypeScript
DESCRIPTION: Defines an interface for RAG retrieval configuration ranking LLM ranker, including the model name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_39

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfigRankingLlmRanker {
    modelName?: string;
}
```

----------------------------------------

TITLE: Defining RealtimeInputConfig Interface in TypeScript
DESCRIPTION: Defines an interface for realtime input configuration, including activity handling, automatic activity detection, and turn coverage.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_42

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RealtimeInputConfig {
    activityHandling?: ActivityHandling;
    automaticActivityDetection?: AutomaticActivityDetection;
    turnCoverage?: TurnCoverage;
}
```

----------------------------------------

TITLE: Defining GenerationConfigRoutingConfigManualRoutingMode Interface in TypeScript
DESCRIPTION: Interface for manual routing mode configuration with specific model name selection.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_36

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerationConfigRoutingConfigManualRoutingMode {
    modelName?: string;
}
```

----------------------------------------

TITLE: Defining Modality Enum in TypeScript
DESCRIPTION: Defines an enum for modalities, including audio, image, and text options.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_57

LANGUAGE: TypeScript
CODE:
```
// @public
export enum Modality {
    // (undocumented)
    AUDIO = "AUDIO",
    // (undocumented)
    IMAGE = "IMAGE",
    // (undocumented)
    MODALITY_UNSPECIFIED = "MODALITY_UNSPECIFIED",
    // (undocumented)
    TEXT = "TEXT"
}
```

----------------------------------------

TITLE: Defining GenerationConfigRoutingConfigAutoRoutingMode Interface in TypeScript
DESCRIPTION: Interface for auto routing mode configuration with preference settings for model quality vs. cost.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_35

LANGUAGE: typescript
CODE:
```
// @public
export interface GenerationConfigRoutingConfigAutoRoutingMode {
    modelRoutingPreference?: 'UNKNOWN' | 'PRIORITIZE_QUALITY' | 'BALANCED' | 'PRIORITIZE_COST';
}
```

----------------------------------------

TITLE: Defining RagRetrievalConfigRankingRankService Interface in TypeScript
DESCRIPTION: Defines an interface for RAG retrieval configuration ranking service, including the model name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_40

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RagRetrievalConfigRankingRankService {
    modelName?: string;
}
```

----------------------------------------

TITLE: Implementing GenerateContentResponsePromptFeedback Class in TypeScript
DESCRIPTION: Defines a class for prompt feedback in content generation responses, including properties for block reason, message, and safety ratings.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_22

LANGUAGE: typescript
CODE:
```
export class GenerateContentResponsePromptFeedback {
    blockReason?: BlockedReason;
    blockReasonMessage?: string;
    safetyRatings?: SafetyRating[];
}
```

----------------------------------------

TITLE: Defining Modality Enum in TypeScript
DESCRIPTION: Defines an enum for modalities, including audio, image, and text types.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_20

LANGUAGE: TypeScript
CODE:
```
// @public
export enum Modality {
    // (undocumented)
    AUDIO = "AUDIO",
    // (undocumented)
    IMAGE = "IMAGE",
    // (undocumented)
    MODALITY_UNSPECIFIED = "MODALITY_UNSPECIFIED",
    // (undocumented)
    TEXT = "TEXT"
}
```

----------------------------------------

TITLE: Defining GenerationConfigRoutingConfigAutoRoutingMode Interface in TypeScript
DESCRIPTION: Specifies an interface for auto routing mode in generation config routing, including an optional property for model routing preference.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_35

LANGUAGE: typescript
CODE:
```
export interface GenerationConfigRoutingConfigAutoRoutingMode {
    modelRoutingPreference?: 'UNKNOWN' | 'PRIORITIZE_QUALITY' | 'BALANCED' | 'PRIORITIZE_COST';
}
```

----------------------------------------

TITLE: Defining LogprobsResult Interface in TypeScript
DESCRIPTION: Defines an interface for logprob results, including chosen candidates and top candidates.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_49

LANGUAGE: TypeScript
CODE:
```
// @public
export interface LogprobsResult {
    chosenCandidates?: LogprobsResultCandidate[];
    topCandidates?: LogprobsResultTopCandidates[];
}
```

----------------------------------------

TITLE: Defining MediaResolution Enum in TypeScript
DESCRIPTION: Defines an enum for media resolutions, including high, medium, and low options.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_56

LANGUAGE: TypeScript
CODE:
```
// @public
export enum MediaResolution {
    // (undocumented)
    MEDIA_RESOLUTION_HIGH = "MEDIA_RESOLUTION_HIGH",
    // (undocumented)
    MEDIA_RESOLUTION_LOW = "MEDIA_RESOLUTION_LOW",
    // (undocumented)
    MEDIA_RESOLUTION_MEDIUM = "MEDIA_RESOLUTION_MEDIUM",
    // (undocumented)
    MEDIA_RESOLUTION_UNSPECIFIED = "MEDIA_RESOLUTION_UNSPECIFIED"
}
```

----------------------------------------

TITLE: Defining RawReferenceImage Interface in TypeScript
DESCRIPTION: Defines an interface for raw reference images, including reference ID, image, and type.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_78

LANGUAGE: TypeScript
CODE:
```
// @public
export interface RawReferenceImage {
    referenceId?: number;
    referenceImage?: Image_2;
    referenceType?: string;
}
```

----------------------------------------

TITLE: Defining FinishReason Enum in TypeScript
DESCRIPTION: Enumeration of reasons why content generation might finish, including safety filters, token limits, and stop sequences.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_13

LANGUAGE: typescript
CODE:
```
// @public
export enum FinishReason {
    // (undocumented)
    BLOCKLIST = "BLOCKLIST",
    // (undocumented)
    FINISH_REASON_UNSPECIFIED = "FINISH_REASON_UNSPECIFIED",
    // (undocumented)
    IMAGE_SAFETY = "IMAGE_SAFETY",
    // (undocumented)
    MALFORMED_FUNCTION_CALL = "MALFORMED_FUNCTION_CALL",
    // (undocumented)
    MAX_TOKENS = "MAX_TOKENS",
    // (undocumented)
    OTHER = "OTHER",
    // (undocumented)
    PROHIBITED_CONTENT = "PROHIBITED_CONTENT",
    // (undocumented)
    RECITATION = "RECITATION",
    // (undocumented)
    SAFETY = "SAFETY",
    // (undocumented)
    SPII = "SPII",
    // (undocumented)
    STOP = "STOP"
}
```

----------------------------------------

TITLE: Defining Pager Class in TypeScript
DESCRIPTION: Defines a generic class for handling paged results, including methods for iterating through pages and accessing individual items.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_30

LANGUAGE: TypeScript
CODE:
```
// @public
export class Pager<T> implements AsyncIterable<T> {
    [Symbol.asyncIterator](): AsyncIterator<T>;
    constructor(name: PagedItem, request: (params: PagedItemConfig) => Promise<PagedItemResponse<T>>, response: PagedItemResponse<T>, params: PagedItemConfig);
    getItem(index: number): T;
    hasNextPage(): boolean;
    // (undocumented)
    protected idxInternal: number;
    get name(): PagedItem;
    nextPage(): Promise<T[]>;
    get page(): T[];
    get pageLength(): number;
    get pageSize(): number;
    get params(): PagedItemConfig;
    // Warning: (ae-forgotten-export) The symbol "PagedItemConfig" needs to be exported by the entry point index.d.ts
    // Warning: (ae-forgotten-export) The symbol "PagedItemResponse" needs to be exported by the entry point index.d.ts
    //
    // (undocumented)
    protected requestInternal: (params: PagedItemConfig) => Promise<PagedItemResponse<T>>;
}
```

----------------------------------------

TITLE: Defining ModalityTokenCount Interface in TypeScript
DESCRIPTION: Defines an interface for modality token counts, including the modality and token count.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_58

LANGUAGE: TypeScript
CODE:
```
// @public
export interface ModalityTokenCount {
    modality?: MediaModality;
    tokenCount?: number;
}
```

----------------------------------------

TITLE: Defining PrebuiltVoiceConfig Interface in TypeScript
DESCRIPTION: Defines an interface for prebuilt voice configuration, including the voice name.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_71

LANGUAGE: TypeScript
CODE:
```
// @public
export interface PrebuiltVoiceConfig {
    voiceName?: string;
}
```

----------------------------------------

TITLE: Defining ExecutableCode Interface in TypeScript
DESCRIPTION: Interface for representing executable code with optional code string and language properties.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_3

LANGUAGE: typescript
CODE:
```
// @public
export interface ExecutableCode {
    code?: string;
    language?: Language;
}
```

----------------------------------------

TITLE: Defining ReplayResponse Class in TypeScript
DESCRIPTION: Defines a class for replay responses, including body segments, headers, SDK response segments, and status code.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_83

LANGUAGE: TypeScript
CODE:
```
// @public
export class ReplayResponse {
    // (undocumented)
    bodySegments?: Record<string, unknown>[];
    // (undocumented)
    headers?: Record<string, string>;
    // (undocumented)
    sdkResponseSegments?: Record<string, unknown>[];
    // (undocumented)
    statusCode?: number;
}
```

----------------------------------------

TITLE: Defining LogprobsResultCandidate Interface in TypeScript
DESCRIPTION: Defines an interface for individual logprob result candidates, including log probability, token, and token ID.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_50

LANGUAGE: TypeScript
CODE:
```
// @public
export interface LogprobsResultCandidate {
    logProbability?: number;
    token?: string;
    tokenId?: number;
}
```

----------------------------------------

TITLE: Defining Operations Class in TypeScript
DESCRIPTION: Defines a class for handling operations, including a method for getting video operations.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_27

LANGUAGE: TypeScript
CODE:
```
// @public (undocumented)
export class Operations extends BaseModule {
    constructor(apiClient: ApiClient);
    getVideosOperation(parameters: types.OperationGetParameters): Promise<types.GenerateVideosOperation>;
}
```

----------------------------------------

TITLE: Declaring FeatureSelectionPreference Enum in TypeScript
DESCRIPTION: Defines an enum for feature selection preferences used in AI model configurations.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_4

LANGUAGE: typescript
CODE:
```
export enum FeatureSelectionPreference {
    BALANCED = "BALANCED",
    FEATURE_SELECTION_PREFERENCE_UNSPECIFIED = "FEATURE_SELECTION_PREFERENCE_UNSPECIFIED",
    PRIORITIZE_COST = "PRIORITIZE_COST",
    PRIORITIZE_QUALITY = "PRIORITIZE_QUALITY"
}
```

----------------------------------------

TITLE: Defining File Interface in TypeScript
DESCRIPTION: Specifies an interface for file metadata, including properties such as creation time, display name, download URI, and various other attributes.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-web.api.md#2025-04-23_snippet_7

LANGUAGE: typescript
CODE:
```
interface File_2 {
    createTime?: string;
    displayName?: string;
    downloadUri?: string;
    error?: FileStatus;
    expirationTime?: string;
    mimeType?: string;
    name?: string;
    sha256Hash?: string;
    sizeBytes?: string;
    source?: FileSource;
    state?: FileState;
    updateTime?: string;
    uri?: string;
    videoMetadata?: Record<string, unknown>;
}
export { File_2 as File }
```

----------------------------------------

TITLE: Defining FeatureSelectionPreference Enum in TypeScript
DESCRIPTION: Enumeration for feature selection preferences with options to prioritize cost, quality, or a balanced approach.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai.api.md#2025-04-23_snippet_4

LANGUAGE: typescript
CODE:
```
// @public
export enum FeatureSelectionPreference {
    // (undocumented)
    BALANCED = "BALANCED",
    // (undocumented)
    FEATURE_SELECTION_PREFERENCE_UNSPECIFIED = "FEATURE_SELECTION_PREFERENCE_UNSPECIFIED",
    // (undocumented)
    PRIORITIZE_COST = "PRIORITIZE_COST",
    // (undocumented)
    PRIORITIZE_QUALITY = "PRIORITIZE_QUALITY"
}
```

----------------------------------------

TITLE: Defining MediaModality Enum in TypeScript
DESCRIPTION: Defines an enum for media modalities, including audio, document, image, text, and video types.
SOURCE: https://github.com/googleapis/js-genai/blob/main/api-report/genai-node.api.md#2025-04-23_snippet_18

LANGUAGE: TypeScript
CODE:
```
// @public
export enum MediaModality {
    // (undocumented)
    AUDIO = "AUDIO",
    // (undocumented)
    DOCUMENT = "DOCUMENT",
    // (undocumented)
    IMAGE = "IMAGE",
    // (undocumented)
    MODALITY_UNSPECIFIED = "MODALITY_UNSPECIFIED",
    // (undocumented)
    TEXT = "TEXT",
    // (undocumented)
    VIDEO = "VIDEO"
}
```