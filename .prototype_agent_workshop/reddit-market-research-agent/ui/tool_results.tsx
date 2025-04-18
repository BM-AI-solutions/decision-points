"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Highlight, themes } from "prism-react-renderer"

// DEPENDS ON SHADCN CARD AND BUTTON, LUCIDE REACT AND PRISM-REACT-RENDERER
interface ToolResult {
  args: Record<string, any>
  result: Record<string, any>
  tool_name: string
}

interface ToolResultsProps {
  data: {
    tool_results: Record<string, ToolResult>
  }
}

const CodeBlock = ({ code }: { code: string }) => (
  <Highlight theme={themes.nightOwl} code={code} language="json">
    {({ style, tokens, getLineProps, getTokenProps }) => (
      <pre style={{ ...style, padding: '1rem', borderRadius: '0.5rem', fontSize: '0.875rem' }}>
        {tokens.map((line, i) => (
          <div key={i} {...getLineProps({ line, key: i })}>
            {line.map((token, key) => (
              <span key={key} {...getTokenProps({ token, key })} />
            ))}
          </div>
        ))}
      </pre>
    )}
  </Highlight>
)

const ToolResultExpander = ({ toolCall, result }: { toolCall: string; result: ToolResult }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className="mb-4 overflow-hidden">
      <CardHeader 
        className="flex flex-row items-center justify-between space-y-0 py-2 bg-gray-100 dark:bg-gray-800 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <CardTitle className="text-base font-medium">Tool call: {result.tool_name}</CardTitle>
        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}>
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </Button>
      </CardHeader>
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[600px]' : 'max-h-0'
        }`}
      >
        <CardContent className="pt-4">
          <div className="mt-2">
            <h4 className="text-sm font-semibold mb-2">Arguments:</h4>
            <CodeBlock code={JSON.stringify(result.args, null, 2)} />
          </div>
          <div className="mt-4">
            <h4 className="text-sm font-semibold mb-2">Results:</h4>
            <div className="max-h-[300px] overflow-y-auto">
              <CodeBlock code={JSON.stringify(result.result, null, 2)} />
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  )
}

export default function ToolResultsExpander({ data }: ToolResultsProps) {
  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold mb-4">Detailed Tool Results</h2>
      {Object.entries(data.tool_results).map(([toolCall, result]) => (
        <ToolResultExpander key={toolCall} toolCall={toolCall} result={result} />
      ))}
    </div>
  )
}

