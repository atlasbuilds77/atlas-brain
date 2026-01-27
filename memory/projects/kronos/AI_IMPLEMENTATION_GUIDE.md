# Kronos AI Implementation Guide
## How to Apply AI SaaS Research to Kronos Dashboard

**Date**: January 26, 2026  
**Purpose**: Practical guide for implementing AI trust features in Kronos

---

## QUICK START: 5 Must-Have AI Features

### 1. **AI Response Card with Citations** (CRITICAL)

```tsx
// components/ai/AIResponseCard.tsx
interface AIResponseProps {
  question: string
  answer: string
  sources: Array<{
    title: string
    url: string
    date: string
    excerpt: string
  }>
  confidence: 'high' | 'medium' | 'low'
  needsReview?: string[]
}

export function AIResponseCard({ 
  question, 
  answer, 
  sources, 
  confidence,
  needsReview 
}: AIResponseProps) {
  return (
    <Card className="border-l-4 border-l-primary-500">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary-600" />
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-600">AI Assistant</span>
            <ConfidenceBadge level={confidence} />
          </div>
          
          <div className="prose prose-sm max-w-none">
            {answer}
          </div>
          
          {/* Sources Section */}
          <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-semibold text-slate-900">Sources:</span>
            </div>
            
            <div className="space-y-2">
              {sources.map((source, i) => (
                <div key={i} className="text-sm">
                  <a 
                    href={source.url}
                    target="_blank"
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    {source.title}
                  </a>
                  <span className="text-slate-500 ml-2">({source.date})</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Needs Review Alert */}
          {needsReview && needsReview.length > 0 && (
            <div className="mt-3 p-3 bg-warning-50 rounded-lg border border-warning-200">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-warning-600 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-warning-900">CPA Review Required:</p>
                  <ul className="text-sm text-warning-700 mt-1 space-y-1">
                    {needsReview.map((item, i) => (
                      <li key={i}>• {item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-2 mt-4">
            <Button variant="primary" size="sm">
              <Copy className="w-4 h-4" />
              Copy Response
            </Button>
            <Button variant="secondary" size="sm">
              <ExternalLink className="w-4 h-4" />
              Verify Sources
            </Button>
            <Button variant="ghost" size="sm">
              <RefreshCw className="w-4 h-4" />
              Regenerate
            </Button>
          </div>
        </div>
      </div>
    </Card>
  )
}
```

---

### 2. **Confidence Badge Component**

```tsx
// components/ai/ConfidenceBadge.tsx
interface ConfidenceBadgeProps {
  level: 'high' | 'medium' | 'low'
  showTooltip?: boolean
}

export function ConfidenceBadge({ level, showTooltip = true }: ConfidenceBadgeProps) {
  const config = {
    high: {
      label: 'High Confidence',
      percentage: '90%+',
      color: 'bg-success-100 text-success-700 border-success-300',
      icon: CheckCircle,
      description: 'Clear IRS guidance found. Safe to use with clients.'
    },
    medium: {
      label: 'Medium Confidence',
      percentage: '60-89%',
      color: 'bg-warning-100 text-warning-700 border-warning-300',
      icon: AlertCircle,
      description: 'Some guidance found. Verify before using.'
    },
    low: {
      label: 'Low Confidence',
      percentage: '<60%',
      color: 'bg-danger-100 text-danger-700 border-danger-300',
      icon: XCircle,
      description: 'Limited guidance. Requires CPA expert judgment.'
    }
  }
  
  const { label, percentage, color, icon: Icon, description } = config[level]
  
  return (
    <Tooltip content={showTooltip ? description : undefined}>
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${color}`}>
        <Icon className="w-3.5 h-3.5" />
        <span className="text-xs font-semibold">{label}</span>
      </div>
    </Tooltip>
  )
}
```

---

### 3. **AI Template Library**

```tsx
// app/ai-templates/page.tsx
const templates = [
  {
    id: 1,
    category: 'Client Communication',
    title: 'Tax Notice Response',
    description: 'Respond to IRS notices with professional tone',
    icon: Mail,
    usageCount: 247,
    prompt: 'Draft a professional response to this IRS notice: [NOTICE DETAILS]',
    tags: ['IRS', 'Client', 'Professional']
  },
  {
    id: 2,
    category: 'Client Communication',
    title: 'Tax Law Explanation',
    description: 'Explain tax law changes in plain language',
    icon: FileText,
    usageCount: 189,
    prompt: 'Explain [TAX LAW/CONCEPT] to my client in simple terms',
    tags: ['Education', 'Client', 'Simplify']
  },
  {
    id: 3,
    category: 'Tax Research',
    title: 'IRS Guidance Search',
    description: 'Find IRS guidance with citations',
    icon: Search,
    usageCount: 156,
    prompt: 'Find IRS guidance on [TAX QUESTION] with citations',
    tags: ['Research', 'IRS', 'Citations']
  },
  // ... more templates
]

export default function AITemplatesPage() {
  const [selectedCategory, setSelectedCategory] = useState('All')
  
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">AI Template Library</h1>
          <p className="mt-2 text-slate-600">
            Pre-built prompts for common tax professional tasks
          </p>
        </div>
        <Button>
          <Plus className="w-5 h-5" />
          Create Custom Template
        </Button>
      </div>
      
      {/* Category Filter */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {['All', 'Client Communication', 'IRS Correspondence', 'Tax Research', 'Document Drafting'].map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              selectedCategory === cat
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>
      
      {/* Popular Templates */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Popular This Week</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map(template => (
            <Card key={template.id} hover className="group cursor-pointer">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <template.icon className="w-6 h-6 text-primary-600" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-900 group-hover:text-primary-600 transition-colors">
                    {template.title}
                  </h3>
                  <p className="text-sm text-slate-600 mt-1">
                    {template.description}
                  </p>
                  
                  <div className="flex items-center gap-2 mt-3">
                    <Badge variant="default" className="text-xs">
                      {template.category}
                    </Badge>
                    <span className="text-xs text-slate-500">
                      Used {template.usageCount} times
                    </span>
                  </div>
                  
                  <Button 
                    variant="primary" 
                    size="sm" 
                    className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Use Template
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
```

---

### 4. **AI Chat Interface**

```tsx
// components/ai/AIChat.tsx
export function AIChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const examplePrompts = [
    "Draft response to CP2000 notice",
    "Explain bonus depreciation to client",
    "What's the 2024 standard mileage rate?",
    "Research home office deduction rules"
  ]
  
  return (
    <Card className="h-[600px] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">AI Tax Assistant</h3>
            <p className="text-xs text-slate-600">Ask me anything about tax law or client communication</p>
          </div>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="font-semibold text-slate-900 mb-2">How can I help you today?</h3>
            <p className="text-sm text-slate-600 mb-4">Try one of these:</p>
            
            <div className="grid grid-cols-2 gap-2 max-w-md mx-auto">
              {examplePrompts.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => setInput(prompt)}
                  className="p-3 text-sm text-left bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' ? (
              <AIResponseCard {...msg.data} />
            ) : (
              <div className="max-w-[70%] bg-primary-600 text-white rounded-2xl px-4 py-3">
                <p className="text-sm">{msg.content}</p>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader className="w-4 h-4 animate-spin text-slate-600" />
                <span className="text-sm text-slate-600">Searching tax law...</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Input */}
      <div className="p-4 border-t border-slate-200">
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about tax law, draft a letter, or research IRS guidance..."
              rows={2}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  // Handle send
                }
              }}
            />
            <p className="text-xs text-slate-500 mt-1 px-1">
              🔒 All queries are encrypted. AI responses include IRS citations.
            </p>
          </div>
          
          <Button size="lg" disabled={!input.trim() || isLoading}>
            <Send className="w-5 h-5" />
            Send
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

---

### 5. **Onboarding Wizard for AI**

```tsx
// components/ai/AIOnboardingWizard.tsx
export function AIOnboardingWizard() {
  const [step, setStep] = useState(1)
  const [preferences, setPreferences] = useState({
    communicationStyle: 'balanced',
    clientTypes: [],
    specialties: []
  })
  
  return (
    <Modal size="lg">
      <div className="p-6">
        {/* Progress */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-600">Step {step} of 3</span>
            <span className="text-sm text-slate-500">{Math.round((step / 3) * 100)}% complete</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all"
              style={{ width: `${(step / 3) * 100}%` }}
            />
          </div>
        </div>
        
        {/* Step 1: See AI Work */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              See AI in Action
            </h2>
            <p className="text-slate-600 mb-6">
              Watch how AI answers tax questions with IRS citations
            </p>
            
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
              <AIResponseCard
                question="What's the 2024 standard mileage rate?"
                answer="The 2024 standard mileage rate for business use is 67 cents per mile."
                sources={[
                  {
                    title: 'IRS Notice 2024-08',
                    url: '#',
                    date: 'Dec 14, 2023',
                    excerpt: 'Standard mileage rates for 2024...'
                  }
                ]}
                confidence="high"
              />
            </div>
            
            <div className="mt-6 flex items-center justify-between">
              <Button variant="ghost" onClick={() => {/* Close */}}>
                Skip Setup
              </Button>
              <Button onClick={() => setStep(2)}>
                Next: Customize AI
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
        
        {/* Step 2: Preferences */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              Customize Your AI Assistant
            </h2>
            <p className="text-slate-600 mb-6">
              Help AI understand your communication style
            </p>
            
            <div className="space-y-6">
              {/* Communication Style */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-3">
                  Communication Style
                </label>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-slate-600">Formal</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={preferences.communicationStyle === 'formal' ? 0 : preferences.communicationStyle === 'balanced' ? 50 : 100}
                    onChange={(e) => {
                      const val = parseInt(e.target.value)
                      setPreferences(p => ({
                        ...p,
                        communicationStyle: val < 33 ? 'formal' : val < 66 ? 'balanced' : 'conversational'
                      }))
                    }}
                    className="flex-1"
                  />
                  <span className="text-sm text-slate-600">Conversational</span>
                </div>
              </div>
              
              {/* Client Types */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-3">
                  Client Types
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['Individual', 'S-Corp', 'C-Corp', 'Partnership', 'Non-Profit', 'Estate'].map(type => (
                    <label key={type} className="flex items-center gap-2 p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm text-slate-900">{type}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex items-center justify-between">
              <Button variant="ghost" onClick={() => setStep(1)}>
                <ChevronLeft className="w-4 h-4" />
                Back
              </Button>
              <Button onClick={() => setStep(3)}>
                Next: Try AI
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
        
        {/* Step 3: First Task */}
        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              Try Your First AI Task
            </h2>
            <p className="text-slate-600 mb-6">
              Pick a template to see AI in action
            </p>
            
            {/* Template selection... */}
            
            <div className="mt-6 flex items-center justify-between">
              <Button variant="ghost" onClick={() => setStep(2)}>
                <ChevronLeft className="w-4 h-4" />
                Back
              </Button>
              <Button variant="primary">
                <CheckCircle className="w-4 h-4" />
                Complete Setup
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}
```

---

## WHERE TO ADD AI FEATURES IN KRONOS

### Dashboard Page
```tsx
// Add AI Quick Actions Card
<Card>
  <CardHeader title="AI Assistant" icon={<Bot />} />
  <div className="mt-4 space-y-2">
    <button className="w-full flex items-center gap-3 p-3 hover:bg-slate-50 rounded-lg">
      <FileText className="w-5 h-5 text-primary-600" />
      <div className="text-left">
        <p className="font-medium text-slate-900">Draft Client Letter</p>
        <p className="text-xs text-slate-500">Explain tax changes in plain language</p>
      </div>
    </button>
    
    <button className="w-full flex items-center gap-3 p-3 hover:bg-slate-50 rounded-lg">
      <Search className="w-5 h-5 text-primary-600" />
      <div className="text-left">
        <p className="font-medium text-slate-900">Research Tax Law</p>
        <p className="text-xs text-slate-500">Find IRS guidance with citations</p>
      </div>
    </button>
    
    <Link href="/ai-chat" className="block">
      <Button variant="primary" fullWidth>
        <MessageSquare className="w-4 h-4" />
        Open AI Chat
      </Button>
    </Link>
  </div>
</Card>
```

### Messages Page
```tsx
// Add AI Draft Assist Button
<Button variant="secondary" onClick={() => setShowAIDraft(true)}>
  <Bot className="w-4 h-4" />
  AI Draft Assist
</Button>

{showAIDraft && (
  <AIResponseCard 
    question="Draft a response explaining bonus depreciation"
    answer="..."
    sources={[...]}
  />
)}
```

### Clients Page
```tsx
// Add AI Client Summary
<Card>
  <CardHeader title="AI Client Summary" />
  <div className="prose prose-sm">
    <p>Based on client history...</p>
  </div>
  <Button variant="ghost" size="sm">
    <RefreshCw className="w-4 h-4" />
    Regenerate Summary
  </Button>
</Card>
```

---

## PRIORITY IMPLEMENTATION ORDER

1. **Week 1**: AI Response Card + Confidence Badges
2. **Week 2**: AI Chat Interface
3. **Week 3**: Template Library
4. **Week 4**: Onboarding Wizard
5. **Week 5**: Integration into existing pages

---

## TESTING CHECKLIST

- [ ] All AI responses show sources
- [ ] Confidence scores display correctly
- [ ] "Needs Review" warnings appear when appropriate
- [ ] Templates work and are customizable
- [ ] Chat interface is responsive
- [ ] Onboarding completes in <5 minutes
- [ ] Mobile layouts work
- [ ] Tooltips are helpful
- [ ] Copy/paste functions work
- [ ] Source links open correctly

---

**Implementation Guide Complete**  
**Next**: Begin Week 1 development
