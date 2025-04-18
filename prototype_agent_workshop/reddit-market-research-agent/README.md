<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

# r/askAgent

Author: [Kai Feinberg](kaifeinberg.dev)

<!-- ABOUT THE PROJECT -->
With more AI generated content every day it has become harder to find reliable information. Many people have turned to Reddit as the last source of human truth. This agent speeds up your research process by identifying relevant reddit posts and extracting insights from the post and comments. This is an easy way to integrate reddit results into your agents and can be combined with youtube search, twitter search, or other apis in order to automate consumer research.

![Reddit Agent Demo](public/reddit_agent_demo.gif)


## What can this agent do?

* Find the best restaurants in Chicago?
* What are the best sci-fi movies?
* Find alternatives to Google Slides?
* What are the best dark academia books?
* Compare housing in SF vs NYC
* Find up and coming indie artists
* What are the best AI code tools for front end?

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Custom UI for tool calls

See the arguments and results from tool calls as well as a custom card for each post fetched by the `search_reddit` tool.

![Reddit ui components](public/reddit_ui_components.gif)

* note that the ui folder is not an app itself just a collection of react components that can be pasted elsewhere

## How does it work

The search process takes place in the `search_reddit` function in the `ai_agent.py` file. It takes in a query which it uses to search the web. It then parse the top links (if the are reddit posts) and extracts the post data and the data from the top (most upvoted) comments.

![How it works](public/how_it_works.png)


*Its worth noting that you can search Reddit via their api or via PRAW. However, it tends to give results that are much less consistent and will often include long posts from subreddits like relationship advice. I think using the Brave search api is a great pattern for integrating search without having to interact with another api. For example you could append "youtube" to the end of a query and get urls of youtube videos all without actual credentials to youtube's api.


## How is this better than Reddit Answers (currently in beta)

* you can combine this with other agents to genenerate reports or complete tasks
* upvotes count is present in the response so you can gauge the authority of a comment
* has chat history so you can find/continue/share your old conversations
* not limited to the US


## Tech Stack

### APIs/integrations
* [Brave Search API](https://brave.com/search/api/)
* [Reddit](https://www.reddit.com/dev/api/) 
* [OpenAI](https://platform.openai.com/docs/overview)

### Libraries used:

* [Pydantic ai](https://github.com/pydantic/pydantic-ai) - to create ai agent with tools
* [Async PRAW](https://asyncpraw.readthedocs.io/en/stable/index.html) - to interact with Reddit's api
* FastAPI - to quickly spin up/host an api


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Note that this doesn't contain code for a full frontend you can interact with. Check out [this repo](https://github.com/kai-feinberg/reddit-agent) if you want a full streamlit interface for your agent.

Edit/add to the ai agent's tools in `ai_agent.py`. If you introduce a new dependency make sure to add it to the context as well in the endpoint file. Highly recommend this video for a more in depth guide: [https://youtu.be/zf_D2Eafvk0?si=Uv0pxXXdEVjDvC6K](https://youtu.be/zf_D2Eafvk0?si=Uv0pxXXdEVjDvC6K)


### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get API Keys for Brave and Reddit (instructions in `.env.example`)
2. Rename `.env.example` to `.env` and add these keys and your open ai api key
3. install the requirements (it is recommended to use a vitual environment such as venv)
```sh
   pip install -r requirements.txt
```
4. run the endpoint
```sh 
python ./agent_endpoint.py
```
5. I recommend using agent 0 to interact with your agent. Follow this guide to get it set up. [https://www.youtube.com/watch?v=7XZbI_ez8_U](https://www.youtube.com/watch?v=7XZbI_ez8_U)


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Custom UI (for a react front end)
When a response is generated with will store a message with this schema

```json
{
  "type": "ai",
  "content": "Agent's response text",
  "data": {
    "...additional info for the frontend..."
  }
}
```

I have modified the endpoint to store the data from tool usage with the following schema in the data field. Args is the arguments used when calling the tool.
Result is the data returned from the tool. Each tool is given a name such as `search_reddit` or `get_weather`. Each tool call is given a unique identifier.

```json
   "tool_results": {
      "TOOL_CALL_IDENTIFIER": {
         "args": {
            "TOOL_ARGUMENTS": "DATA"
         },
         "result": {
            "TOOL_DATA": "DATA"
         },
         "tool_name": "MY_TOOL"
      },
      call___XXXXX {..}
   }
```

<!-- Start of Selection -->
<details>
  <summary>CLICK FOR EXAMPLE DATA</summary>

  ```json
  "tool_results": {
      "call_0tNO9fe3yKtsWQnM5jq406xr": {
        "args": {
          "query": "minecraft"
        },
        "result": {
          "subreddits": ["Minecraft", "MinecraftMemes", "MinecraftBuddies", "Minecraftbuilds", "teenagers"]
        },
        "tool_name": "find_subreddits"
      },
      "call_1xYZ9ab3cDtsWQnM5jq406yz": {
        "args": {
          "city": "New York",
          "date": "2023-05-15"
        },
        "result": {
          "temperature": 72,
          "conditions": "Partly cloudy",
          "humidity": 65
        },
        "tool_name": "get_weather"
      }
  }
  ```

</details>


There are two react components in the `/ui` folder making use of this tool data.

`tool_results.tsx` takes any message and renders the tools used and each tools arguments and returned content

`reddit_result.tsx` renders cards for any reddit posts that were fetched with the search reddit tool.

I created these using v0 and you can see the chat here: [https://v0.dev/chat/tool-results-expander-D78mKUcHhDM](https://v0.dev/chat/tool-results-expander-D78mKUcHhDM)

Here is an example of how the components look
![Reddit ui components](public/reddit_ui_components.gif)


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Absolutely enormous shoutout to Cole Medin for putting on this hackathon and providing the resources/help to make some really cool agents.

Here's his template for creating agents with python, pydantic, and supabase.

[https://github.com/coleam00/ottomator-agents/blob/main/~sample-python-agent~/sample_supabase_agent.py](https://github.com/coleam00/ottomator-agents/blob/main/~sample-python-agent~/sample_supabase_agent.py)

Here is his super helpful developer guide:
[https://studio.ottomator.ai/guide](https://studio.ottomator.ai/guide)

Cole also has countless videos on his channel that are super handy for building ai agents both with pydantic and no code/low code tools:
[Cole's youtube channel](https://www.youtube.com/@ColeMedin)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. Feel free to clone it, distribute it, and do whatever. Pls credit me/hire me I'm just a poor college student lmao

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Kai Feinberg - [kaifeinberg.dev](https://www.kaifeinberg.dev/)


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

This agent is part of the oTTomator agents collection. For contributions or issues, please refer to the main repository guidelines.





