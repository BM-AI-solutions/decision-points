import { RedditResultsGrid } from "@/components/RedditResultsGrid"
import ToolResultsExpander from "@/components/ToolResultsExpander"

const dummyData = {
  tool_results: {
    call_0tNO9fe3yKtsWQnM5jq406xr: {
      args: {
        query: "minecraft",
      },
      result: {
        subreddits: ["Minecraft", "MinecraftMemes", "MinecraftBuddies", "Minecraftbuilds", "teenagers"],
      },
      tool_name: "find_subreddits",
    },
    call_1xYZ9ab3cDtsWQnM5jq406yz: {
      args: {
        city: "New York",
        date: "2023-05-15",
      },
      result: {
        temperature: 72,
        conditions: "Partly cloudy",
        humidity: 65,
      },
      tool_name: "get_weather",
    },
    call_2ABC3de4fGhiJKlM7nop8qrs: {
      args: {
        query: "artificial intelligence",
      },
      result: {
        results: [
          {
            title: "The Future of AI: Opportunities and Challenges",
            subreddit: "artificial",
            score: 1520,
            num_comments: 237,
            selftext: "As AI continues to advance at an unprecedented pace, we find ourselves at a crossroads...",
            url: "https://www.reddit.com/r/artificial/comments/example1",
            comments: [
              {
                author: "AI_Enthusiast",
                score: 305,
                body: "Great post! I think one of the biggest challenges we face is ensuring AI remains ethical and aligned with human values."
              },
              {
                author: "FutureTech",
                score: 189,
                body: "The potential applications in healthcare are particularly exciting. Imagine AI systems that can diagnose diseases more accurately than human doctors!"
              }
            ]
          },
          {
            title: "How Machine Learning is Revolutionizing Scientific Research",
            subreddit: "MachineLearning",
            score: 982,
            num_comments: 145,
            selftext: "From particle physics to climate science, machine learning algorithms are accelerating discoveries across various scientific disciplines...",
            url: "https://www.reddit.com/r/MachineLearning/comments/example2",
            comments: [
              {
                author: "DataScientist123",
                score: 201,
                body: "As someone working in the field, I can attest to the massive impact ML is having. It's not just speeding up research, but also uncovering patterns we might have missed otherwise."
              },
              {
                author: "AISkeptic",
                score: 87,
                body: "While the potential is undeniable, we should also be cautious about over-relying on ML. It's crucial to maintain human oversight and interpretation of results."
              }
            ]
          }
        ]
      },
      tool_name: "search_reddit",
    }
  },
}

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <main className="container mx-auto p-4 md:p-8">
        <h1 className="text-4xl font-bold mb-8 text-center">Tool Results Dashboard</h1>
        <div className="space-y-12">
          <RedditResultsGrid data={dummyData} />
          <ToolResultsExpander data={dummyData} />
        </div>
      </main>
    </div>
  )
}

