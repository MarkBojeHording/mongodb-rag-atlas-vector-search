/// <reference types="vite/client" />

import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, FileText, Clock } from 'lucide-react';

interface Source {
  document: string;
  page: number;
  relevance: number;
  chunk: string;
  metadata?: {
    source?: string;
    page_number?: number;
    url?: string;
  };
  page_content: string;
}

interface Message {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources: Source[];
}

const API_BASE_URL = '/api';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'assistant',
      content: "Hello! I'm your RAG Assistant. How can I assist you today?",
      timestamp: new Date(),
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sampleQuestions = [
    "How is Atlas Stream Processing performing?",
    "What are the key financial highlights from the latest quarter?",
    "Tell me about our cloud strategy"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: text,
      timestamp: new Date(),
      sources: []
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
    }

    setIsLoading(false);
  };

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white text-xl font-semibold">RAG Assistant</h1>
            <p className="text-gray-400 text-sm">Powered by AI-model: nomic-embed-text-v1</p>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl ${message.type === 'user' ? 'bg-blue-600' : 'bg-gray-700'} rounded-2xl px-4 py-3`}>
              {/* Render answer with line breaks */}
              <div className="text-white whitespace-pre-line">{message.content}</div>

              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-600">
                  <p className="text-gray-300 text-sm font-medium mb-2">Sources:</p>
                  <div className="space-y-2">
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="bg-gray-600 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-green-400 font-medium text-sm">{source.metadata?.source || 'Source'}</span>
                            {source.metadata?.url && (
                              <a
                                href={source.metadata.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-400 hover:text-blue-300 text-xs underline"
                              >
                                View PDF
                              </a>
                            )}
                          </div>
                          {source.metadata?.page_number !== undefined && source.metadata?.page_number !== null && (
                            <span className="text-gray-400 text-xs">Page {source.metadata.page_number}</span>
                          )}
                        </div>
                        <p className="text-gray-300 text-sm">{source.page_content.slice(0, 200)}...</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center mt-2 text-gray-400 text-xs">
                <Clock className="w-3 h-3 mr-1" />
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {/* Loading */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 rounded-2xl px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-gray-400 text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Sample Questions */}
      {messages.length === 1 && (
        <div className="px-6 pb-4">
          <div className="flex flex-wrap gap-2">
            {sampleQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(question)}
                className="bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-2 rounded-lg text-sm transition-colors border border-gray-600"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-700 px-6 py-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask about our financials, AI initiatives, partnerships."
              className="w-full bg-gray-800 text-white border border-gray-600 rounded-xl px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="absolute right-2 bottom-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white p-2 rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <button className="bg-gray-800 hover:bg-gray-700 text-gray-300 p-3 rounded-xl border border-gray-600 transition-colors">
            <Upload className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
