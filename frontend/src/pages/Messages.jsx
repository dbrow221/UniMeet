import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api';
import '../styles/Messages.css';

const Messages = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState(null);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Get current user ID from token
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setCurrentUserId(payload.user_id);
      } catch (err) {
        console.error('Failed to decode token:', err);
      }
    }

    fetchConversations();
    
    // Check if there's a userId in URL params (for starting new conversation)
    const userId = searchParams.get('userId');
    if (userId) {
      const user = { id: parseInt(userId), username: searchParams.get('username') || 'User' };
      handleSelectUser(user);
    }
  }, [searchParams]);

  // Poll for new messages every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchConversations();
      if (selectedUser) {
        fetchMessages(selectedUser.id);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedUser]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/messages/conversations/');
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (userId) => {
    try {
      const response = await api.get(`/api/messages/thread/${userId}/`);
      setMessages(response.data);
      
      // Mark messages as read
      await api.post(`/api/messages/mark-read/${userId}/`);
      
      // Update conversations to reflect read status
      fetchConversations();
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSelectUser = async (user) => {
    setSelectedUser(user);
    await fetchMessages(user.id);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !selectedUser) return;

    try {
      await api.post('/api/messages/send/', {
        recipient: selectedUser.id,
        content: newMessage
      });

      setNewMessage('');
      await fetchMessages(selectedUser.id);
      await fetchConversations();
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    }
  };

  if (loading) {
    return <div className="messages-loading">Loading messages...</div>;
  }

  return (
    <div className="messages-container">
      <div className="conversations-sidebar">
        <h2>Messages</h2>
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>No messages yet</p>
            <button onClick={() => navigate('/users/search')} className="start-conversation-btn">
              Find Friends to Message
            </button>
          </div>
        ) : (
          <div className="conversations-list">
            {conversations.map((conversation) => (
              <div
                key={conversation.user.id}
                className={`conversation-item ${selectedUser?.id === conversation.user.id ? 'active' : ''}`}
                onClick={() => handleSelectUser(conversation.user)}
              >
                <div className="conversation-info">
                  <div className="conversation-header">
                    <span className="conversation-username">{conversation.user.username}</span>
                    {conversation.unread_count > 0 && (
                      <span className="unread-badge">{conversation.unread_count}</span>
                    )}
                  </div>
                  {conversation.last_message && (
                    <p className="last-message">
                      {conversation.last_message.sender_id === currentUserId ? 'You: ' : ''}
                      {conversation.last_message.content.substring(0, 50)}
                      {conversation.last_message.content.length > 50 ? '...' : ''}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="chat-area">
        {selectedUser ? (
          <>
            <div className="chat-header">
              <h3>{selectedUser.username}</h3>
              <button onClick={() => navigate(`/user/${selectedUser.id}`)} className="view-profile-btn">
                View Profile
              </button>
            </div>

            <div className="messages-list">
              {messages.length === 0 ? (
                <div className="no-messages">
                  <p>No messages yet. Start the conversation!</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`message ${message.sender === currentUserId ? 'sent' : 'received'}`}
                  >
                    <div className="message-content">
                      <p>{message.content}</p>
                      <span className="message-time">
                        {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSendMessage} className="message-input-form">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                className="message-input"
              />
              <button type="submit" disabled={!newMessage.trim()} className="send-btn">
                Send
              </button>
            </form>
          </>
        ) : (
          <div className="no-chat-selected">
            <p>Select a conversation to start messaging</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Messages;
