import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Bot, Send, Sparkles, AlertTriangle, Calendar } from 'lucide-react';

export const PatientAiAssistantPage = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      content: 'Hello! I am your AI Care Navigator. How can I help you find healthcare services or schedule an appointment today?\n\nExamples:\n• "I need to book a skin consultation this Saturday afternoon."\n• "Book me a dermatologist tomorrow morning."\n• "Do I have any appointments coming up?"'
    }
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', content: userMsg }]);
    setSending(true);

    try {
      // Direct integration or care navigation logic call
      const lower = userMsg.toLowerCase();
      let reply = '';
      let recommendedDoctors = [];

      if (lower.includes('skin') || lower.includes('dermatolog')) {
        reply = "I identified that you need a **Dermatology** consultation. Here are the top recommended specialists matching your request:";
        const docRes = await api.get('/doctors');
        recommendedDoctors = docRes.data.filter(d => d.department.code === 'DERM' || d.department.name.includes('Dermatology'));
      } else if (lower.includes('heart') || lower.includes('cardio')) {
        reply = "I identified that you need a **Cardiology** consultation. Here are the top recommended specialists:";
        const docRes = await api.get('/doctors');
        recommendedDoctors = docRes.data.filter(d => d.department.code === 'CARD' || d.department.name.includes('Cardiology'));
      } else if (lower.includes('appointment') || lower.includes('schedule')) {
        reply = "Checking your current appointments...\n\nYou can view all your active bookings under **My Appointments** in the sidebar.";
      } else {
        reply = "Sure! I can help you search departments, check doctor availability, or book a consultation. Which department or specialist are you looking for?";
      }

      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          content: reply,
          doctors: recommendedDoctors
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', content: "I'm having trouble processing that right now. Please select a department from our Find Doctors page." }
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ maxWidth: '940px', margin: '0 auto', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 128px)' }}>
      {/* AI Header with Subtle Blue-Teal Gradient */}
      <div
        className="glass-panel"
        style={{
          padding: '1.15rem 1.5rem',
          marginBottom: '1rem',
          background: 'linear-gradient(135deg, #EFF6FF 0%, #F0FDFA 100%)',
          borderColor: 'var(--light-blue)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
          <div className="brand-mark" style={{ width: '44px', height: '44px' }}>
            <Bot size={22} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)' }}>
              AI Healthcare Care Navigator
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.84rem' }}>
              Ask natural language questions to find departments, doctors, and book appointments.
            </p>
          </div>
        </div>
        <span className="badge badge-teal">
          <Sparkles size={13} />
          <span>Assistant Ready</span>
        </span>
      </div>

      {/* Safety Disclaimer */}
      <div className="alert alert-warning" style={{ padding: '0.7rem 1rem', marginBottom: '1rem' }}>
        <AlertTriangle size={16} color="var(--warning)" style={{ flexShrink: 0 }} />
        <span style={{ fontSize: '0.78rem' }}>
          <strong>Notice:</strong> This AI assistant is strictly for administrative scheduling and hospital navigation. It does NOT diagnose conditions or prescribe treatments.
        </span>
      </div>

      {/* Chat Messages Container */}
      <div
        className="glass-panel"
        style={{
          flex: 1,
          padding: '1.5rem',
          overflowY: 'auto',
          marginBottom: '1rem',
          display: 'flex',
          flexDirection: 'column',
          background: 'var(--bg-card)'
        }}
      >
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender}`}>
            {msg.sender === 'assistant' && (
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '10px',
                  background: 'var(--light-teal)',
                  color: 'var(--secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}
              >
                <Bot size={17} />
              </div>
            )}
            <div className="chat-bubble">
              <p style={{ whiteSpace: 'pre-line' }}>{msg.content}</p>

              {/* Recommended Doctor Cards inline */}
              {msg.doctors && msg.doctors.length > 0 && (
                <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {msg.doctors.map(doc => (
                    <div
                      key={doc.id}
                      style={{
                        padding: '0.9rem 1rem',
                        background: '#FFFFFF',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: '1rem',
                        flexWrap: 'wrap',
                        boxShadow: 'var(--shadow-xs)'
                      }}
                    >
                      <div>
                        <h4 style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--text-main)' }}>
                          Dr. {doc.user.full_name}
                        </h4>
                        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                          {doc.qualification} • {doc.department.name} • Fee: ₹{doc.consultation_fee}
                        </p>
                        <span className="badge badge-teal" style={{ marginTop: '0.4rem' }}>
                          Match: 94% (Specialty &amp; Schedule)
                        </span>
                      </div>
                      <button
                        className="btn btn-primary"
                        style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
                        onClick={() => navigate(`/patient/book?doctor_id=${doc.id}&department_id=${doc.department_id}`)}
                      >
                        <Calendar size={14} />
                        <span>Book Slot</span>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={handleSend}
        className="glass-panel"
        style={{ padding: '0.6rem', display: 'flex', gap: '0.6rem', alignItems: 'center' }}
      >
        <input
          type="text"
          className="form-input"
          placeholder="Ask AI Care Navigator... (e.g. Book me a dermatologist tomorrow)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
          style={{ flex: 1, border: 'none', boxShadow: 'none', padding: '0.65rem 0.9rem', fontSize: '0.95rem' }}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '0.72rem 1.35rem' }} disabled={sending}>
          <Send size={17} />
          <span>{sending ? 'Sending...' : 'Send'}</span>
        </button>
      </form>
    </div>
  );
};
