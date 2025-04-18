import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowBigUp, MessageSquare } from 'lucide-react'
import Link from 'next/link'

interface RedditPost {
  title: string
  subreddit: string
  score: number
  num_comments: number
  selftext: string
  url: string
  comments: {
    author: string | null
    score: number
    body: string
  }[]
}

interface ToolResult {
  args: Record<string, any>
  result: Record<string, any>
  tool_name: string
}

interface RedditResultsGridProps {
  data: {
    tool_results: Record<string, ToolResult>
  }
}

function RedditPostCard({ post }: { post: RedditPost }) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="p-3">
        <CardTitle className="text-sm line-clamp-2">
          <Link href={post.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
            {post.title}
          </Link>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0 flex-grow flex flex-col justify-between">
        <div className="flex items-center space-x-2 text-xs text-muted-foreground mb-2">
          <span className="truncate">r/{post.subreddit}</span>
          <span className="flex items-center whitespace-nowrap">
            <ArrowBigUp className="w-3 h-3 mr-1" />
            {post.score}
          </span>
          <span className="flex items-center whitespace-nowrap">
            <MessageSquare className="w-3 h-3 mr-1" />
            {post.num_comments}
          </span>
        </div>
        {post.selftext && (
          <p className="text-xs line-clamp-2">{post.selftext}</p>
        )}
      </CardContent>
    </Card>
  )
}

export function RedditResultsGrid({ data }: RedditResultsGridProps) {
  const redditResults = Object.values(data.tool_results).find(result => result.tool_name === 'search_reddit')?.result.results || []

  if (redditResults.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Reddit Search Results</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {redditResults.map((post, index) => (
          <RedditPostCard key={index} post={post} />
        ))}
      </div>
    </div>
  )
}

