import { useCallback, useEffect, useRef, useState } from "react";
import { Plus, Send, Trash2 } from "lucide-react";
import api from "../services/api";
import type { Conversation, Message } from "../types";

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadConversations = useCallback(async () => {
    const { data } = await api.get<Conversation[]>("/chat/conversations");
    setConversations(data);
    if (data.length && !activeId) setActiveId(data[0].id);
  }, [activeId]);

  const loadMessages = useCallback(async (id: number) => {
    setLoading(true);
    try {
      const { data } = await api.get<Message[]>(`/chat/conversations/${id}/messages`);
      setMessages(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (activeId) loadMessages(activeId);
  }, [activeId, loadMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const newChat = async () => {
    const { data } = await api.post<Conversation>("/chat/conversations", { title: "New Chat" });
    setConversations((prev) => [data, ...prev]);
    setActiveId(data.id);
    setMessages([]);
  };

  const deleteChat = async (id: number) => {
    await api.delete(`/chat/conversations/${id}`);
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeId === id) {
      setActiveId(null);
      setMessages([]);
    }
  };

  const send = async () => {
    if (!input.trim() || !activeId || sending) return;
    const text = input.trim();
    setInput("");
    setSending(true);

    const tempUser: Message = {
      id: Date.now(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUser]);

    try {
      const { data } = await api.post(`/chat/conversations/${activeId}/messages`, {
        message: text,
      });
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUser.id),
        tempUser,
        data.message,
      ]);
      loadConversations();
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== tempUser.id));
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="w-72 border-r border-slate-800 flex flex-col bg-slate-900/30">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h2 className="font-semibold">Conversations</h2>
          <button onClick={newChat} className="p-2 hover:bg-slate-800 rounded-lg" title="New chat">
            <Plus className="w-5 h-5 text-brand-400" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((c) => (
            <div
              key={c.id}
              className={`group flex items-center gap-1 rounded-lg ${
                activeId === c.id ? "bg-brand-600/20" : "hover:bg-slate-800"
              }`}
            >
              <button
                onClick={() => setActiveId(c.id)}
                className="flex-1 text-left px-3 py-2 text-sm truncate"
              >
                {c.title}
              </button>
              <button
                onClick={() => deleteChat(c.id)}
                className="opacity-0 group-hover:opacity-100 p-2 text-slate-500 hover:text-red-400"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          {!conversations.length && (
            <p className="text-sm text-slate-500 p-3">No conversations yet</p>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {!activeId ? (
          <div className="flex-1 flex items-center justify-center text-slate-500">
            <div className="text-center">
              <p className="mb-4">Start a new conversation</p>
              <button onClick={newChat} className="btn-primary">
                New Chat
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {loading ? (
                <p className="text-slate-500 text-center">Loading...</p>
              ) : (
                messages.map((m) => (
                  <div
                    key={m.id}
                    className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                        m.role === "user"
                          ? "bg-brand-600 text-white"
                          : "bg-slate-800 text-slate-100 border border-slate-700"
                      }`}
                    >
                      {m.content}
                      {m.sources && m.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-600 text-xs text-slate-400">
                          Sources: {m.sources.map((s) => s.source).join(", ")}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              <div ref={bottomRef} />
            </div>

            <div className="p-4 border-t border-slate-800">
              <div className="flex gap-2 max-w-4xl mx-auto">
                <input
                  className="input-field flex-1"
                  placeholder="Ask about your documents..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), send())}
                  disabled={sending}
                />
                <button onClick={send} className="btn-primary px-4" disabled={sending || !input.trim()}>
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
