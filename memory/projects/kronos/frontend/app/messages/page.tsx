'use client'

import { useState } from 'react'
import { Card, CardHeader, EmptyStateCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  MessageSquare,
  Search,
  Plus,
  Send,
  Paperclip,
  MoreVertical,
  Star,
  Archive,
  Trash2,
  Clock,
  CheckCheck,
  Circle
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

const conversations = [
  {
    id: 1,
    clientName: 'Michael Chen',
    clientInitials: 'MC',
    lastMessage: 'Thanks for sending over the tax organizer. I\'ll complete it by end of week.',
    timestamp: '2024-01-26T14:30:00',
    unread: 2,
    starred: false,
    status: 'active',
  },
  {
    id: 2,
    clientName: 'Sarah Johnson',
    clientInitials: 'SJ',
    lastMessage: 'I have a question about the deductions we discussed last time.',
    timestamp: '2024-01-26T11:15:00',
    unread: 1,
    starred: true,
    status: 'urgent',
  },
  {
    id: 3,
    clientName: 'ABC Corporation',
    clientInitials: 'AC',
    lastMessage: 'All Q4 documents have been uploaded to the portal.',
    timestamp: '2024-01-25T16:45:00',
    unread: 0,
    starred: false,
    status: 'active',
  },
  {
    id: 4,
    clientName: 'David Wilson',
    clientInitials: 'DW',
    lastMessage: 'Great, I\'ll schedule a call for next week. Thanks!',
    timestamp: '2024-01-24T09:20:00',
    unread: 0,
    starred: false,
    status: 'active',
  },
  {
    id: 5,
    clientName: 'Emily Rodriguez',
    clientInitials: 'ER',
    lastMessage: 'Can we discuss R&D tax credits for my company?',
    timestamp: '2024-01-23T13:30:00',
    unread: 3,
    starred: true,
    status: 'urgent',
  },
]

const messages = [
  {
    id: 1,
    sender: 'Michael Chen',
    isClient: true,
    content: 'Hi Laura, I received the tax organizer. Quick question - do I need to include my 1099s from freelance work?',
    timestamp: '2024-01-26T13:15:00',
    status: 'delivered',
  },
  {
    id: 2,
    sender: 'You',
    isClient: false,
    content: 'Yes, please include all 1099 forms you received. They\'re essential for reporting your freelance income accurately.',
    timestamp: '2024-01-26T13:20:00',
    status: 'read',
  },
  {
    id: 3,
    sender: 'Michael Chen',
    isClient: true,
    content: 'Perfect, I\'ll gather those. Also, I started a side LLC this year - should I mention that?',
    timestamp: '2024-01-26T13:25:00',
    status: 'delivered',
  },
  {
    id: 4,
    sender: 'You',
    isClient: false,
    content: 'Definitely! We\'ll need to discuss the LLC structure and whether you want to make an S-Corp election. Let\'s schedule a call to review this.',
    timestamp: '2024-01-26T13:28:00',
    status: 'read',
  },
  {
    id: 5,
    sender: 'Michael Chen',
    isClient: true,
    content: 'Thanks for sending over the tax organizer. I\'ll complete it by end of week.',
    timestamp: '2024-01-26T14:30:00',
    status: 'delivered',
  },
]

export default function MessagesPage() {
  const [selectedConversation, setSelectedConversation] = useState(conversations[0])
  const [messageText, setMessageText] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const hasMessages = conversations.length > 0
  const unreadCount = conversations.reduce((sum, conv) => sum + conv.unread, 0)

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Messages</h1>
          <p className="mt-2 text-slate-600">
            Communicate with your clients in one secure place
          </p>
          {unreadCount > 0 && (
            <div className="mt-3 flex items-center gap-2">
              <Badge variant="danger">{unreadCount} unread</Badge>
              <span className="text-sm text-slate-500">messages</span>
            </div>
          )}
        </div>
        <Button size="lg">
          <Plus className="w-5 h-5" />
          New Message
        </Button>
      </div>

      {!hasMessages ? (
        <EmptyStateCard
          title="No messages yet"
          description="Start a conversation with your clients. Send updates, answer questions, and keep everything organized in one place."
          icon={<MessageSquare className="w-12 h-12 text-slate-400" />}
          action={
            <Button size="lg">
              <Plus className="w-5 h-5" />
              Send Your First Message
            </Button>
          }
        />
      ) : (
        <Card padding="none" className="h-[calc(100vh-280px)]">
          <div className="flex h-full">
            {/* Conversations List */}
            <div className="w-96 border-r border-slate-200 flex flex-col">
              {/* Search */}
              <div className="p-4 border-b border-slate-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search messages..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Conversation Items */}
              <div className="flex-1 overflow-y-auto">
                {conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    onClick={() => setSelectedConversation(conversation)}
                    className={`w-full p-4 flex items-start gap-3 hover:bg-slate-50 transition-colors border-b border-slate-100 ${
                      selectedConversation?.id === conversation.id
                        ? 'bg-primary-50 border-l-4 border-l-primary-600'
                        : ''
                    }`}
                  >
                    {/* Avatar */}
                    <div className="relative flex-shrink-0">
                      <div className={`w-12 h-12 rounded-full ${
                        conversation.unread > 0
                          ? 'bg-gradient-to-br from-primary-500 to-primary-600'
                          : 'bg-gradient-to-br from-slate-400 to-slate-500'
                      } flex items-center justify-center text-white font-semibold`}>
                        {conversation.clientInitials}
                      </div>
                      {conversation.unread > 0 && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-danger-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                          {conversation.unread}
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0 text-left">
                      <div className="flex items-center justify-between mb-1">
                        <p className={`font-semibold truncate ${
                          conversation.unread > 0 ? 'text-slate-900' : 'text-slate-700'
                        }`}>
                          {conversation.clientName}
                        </p>
                        <span className="text-xs text-slate-500 flex-shrink-0 ml-2">
                          {new Date(conversation.timestamp).toLocaleTimeString('en-US', { 
                            hour: 'numeric', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </div>
                      <p className={`text-sm truncate ${
                        conversation.unread > 0 ? 'text-slate-900 font-medium' : 'text-slate-600'
                      }`}>
                        {conversation.lastMessage}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        {conversation.starred && (
                          <Star className="w-3.5 h-3.5 text-warning-500 fill-warning-500" />
                        )}
                        {conversation.status === 'urgent' && (
                          <Badge variant="danger" className="text-xs">Urgent</Badge>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Message Thread */}
            <div className="flex-1 flex flex-col">
              {/* Thread Header */}
              <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white font-semibold">
                    {selectedConversation.clientInitials}
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900">
                      {selectedConversation.clientName}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Circle className="w-2 h-2 text-success-500 fill-success-500" />
                      <span>Active</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm">
                    <Star className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Archive className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isClient ? 'justify-start' : 'justify-end'}`}
                  >
                    <div className={`max-w-[70%] ${message.isClient ? 'order-1' : 'order-2'}`}>
                      {/* Message Bubble */}
                      <div className={`rounded-2xl px-4 py-3 ${
                        message.isClient
                          ? 'bg-white border border-slate-200'
                          : 'bg-primary-600 text-white'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                      </div>
                      
                      {/* Timestamp & Status */}
                      <div className={`flex items-center gap-2 mt-1 px-2 ${
                        message.isClient ? 'justify-start' : 'justify-end'
                      }`}>
                        <span className="text-xs text-slate-500">
                          {new Date(message.timestamp).toLocaleTimeString('en-US', { 
                            hour: 'numeric', 
                            minute: '2-digit' 
                          })}
                        </span>
                        {!message.isClient && (
                          <CheckCheck className={`w-3.5 h-3.5 ${
                            message.status === 'read' ? 'text-primary-600' : 'text-slate-400'
                          }`} />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-slate-200 bg-white">
                <div className="flex items-end gap-3">
                  <Button variant="ghost" size="sm">
                    <Paperclip className="w-5 h-5" />
                  </Button>
                  
                  <div className="flex-1">
                    <textarea
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      placeholder="Type your message..."
                      rows={2}
                      className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                    />
                  </div>

                  <Button 
                    size="lg"
                    disabled={!messageText.trim()}
                  >
                    <Send className="w-5 h-5" />
                    Send
                  </Button>
                </div>
                
                <p className="text-xs text-slate-500 mt-2 px-2">
                  All messages are encrypted and secure. Press Enter to send, Shift+Enter for new line.
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
