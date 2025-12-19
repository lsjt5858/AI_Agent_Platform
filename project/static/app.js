/**
 * AI Agent Platform - Frontend Application
 * 
 * Implements:
 * - Agent list and creation (Requirements: 6.1, 6.5)
 * - Conversation interface (Requirements: 6.2, 6.3, 6.4)
 * - API integration and state management (Requirements: 6.2, 6.3)
 */

// =============================================================================
// API Client
// =============================================================================

const API_BASE = '/api';

class ApiClient {
    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise<object>} - API response data
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                const errorMessage = data.error?.message || data.detail?.error?.message || 'Request failed';
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            if (error.name === 'TypeError') {
                throw new Error('Network error. Please check your connection.');
            }
            throw error;
        }
    }

    // Agent APIs
    async getAgents() {
        return this.request('/agents');
    }

    async getAgent(agentId) {
        return this.request(`/agents/${agentId}`);
    }

    async createAgent(data) {
        return this.request('/agents', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateAgent(agentId, data) {
        return this.request(`/agents/${agentId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteAgent(agentId) {
        return this.request(`/agents/${agentId}`, {
            method: 'DELETE',
        });
    }


    // Conversation APIs
    async getConversations(agentId) {
        return this.request(`/agents/${agentId}/conversations`);
    }

    async createConversation(agentId, data = {}) {
        return this.request(`/agents/${agentId}/conversations`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getConversation(conversationId) {
        return this.request(`/conversations/${conversationId}`);
    }

    async deleteConversation(conversationId) {
        return this.request(`/conversations/${conversationId}`, {
            method: 'DELETE',
        });
    }

    // Message APIs
    async getMessages(conversationId) {
        return this.request(`/conversations/${conversationId}/messages`);
    }

    async sendMessage(conversationId, content) {
        return this.request(`/conversations/${conversationId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
    }
}

const api = new ApiClient();

// =============================================================================
// State Management
// =============================================================================

const state = {
    agents: [],
    currentAgent: null,
    conversations: [],
    currentConversation: null,
    messages: [],
    isLoading: false,
    editingAgentId: null,
};

// =============================================================================
// UI Utilities
// =============================================================================

function showLoading() {
    state.isLoading = true;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    state.isLoading = false;
    document.getElementById('loading-overlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}


// =============================================================================
// Agent List Rendering (Requirements: 6.1)
// =============================================================================

function renderAgentList() {
    const container = document.getElementById('agent-list');
    
    if (state.agents.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>暂无 Agent</p>
                <p>点击上方按钮创建</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.agents.map(agent => `
        <div class="agent-item ${state.currentAgent?.id === agent.id ? 'active' : ''}" 
             data-agent-id="${agent.id}">
            <div class="agent-item-name">${escapeHtml(agent.name)}</div>
            <div class="agent-item-description">${escapeHtml(agent.description || '无描述')}</div>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.agent-item').forEach(item => {
        item.addEventListener('click', () => {
            const agentId = parseInt(item.dataset.agentId);
            selectAgent(agentId);
        });
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadAgents() {
    try {
        const response = await api.getAgents();
        state.agents = response.data || [];
        renderAgentList();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function selectAgent(agentId) {
    const agent = state.agents.find(a => a.id === agentId);
    if (!agent) return;

    state.currentAgent = agent;
    state.currentConversation = null;
    state.messages = [];

    // Update UI
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('chat-container').style.display = 'grid';
    document.getElementById('current-agent-name').textContent = agent.name;
    document.getElementById('current-agent-description').textContent = agent.description || '无描述';

    renderAgentList();
    await loadConversations();
    renderMessages();
    updateMessageInput();
}

// =============================================================================
// Agent CRUD Operations (Requirements: 6.5)
// =============================================================================

function openAgentModal(agentId = null) {
    state.editingAgentId = agentId;
    const modal = document.getElementById('agent-modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('agent-form');

    if (agentId) {
        const agent = state.agents.find(a => a.id === agentId);
        if (agent) {
            title.textContent = '编辑 Agent';
            document.getElementById('agent-name').value = agent.name;
            document.getElementById('agent-system-prompt').value = agent.system_prompt;
            document.getElementById('agent-description').value = agent.description || '';
        }
    } else {
        title.textContent = '创建新 Agent';
        form.reset();
        document.getElementById('agent-system-prompt').value = 'You are a helpful assistant.';
    }

    modal.style.display = 'flex';
}

function closeAgentModal() {
    document.getElementById('agent-modal').style.display = 'none';
    state.editingAgentId = null;
}

async function saveAgent(event) {
    event.preventDefault();

    const name = document.getElementById('agent-name').value.trim();
    const systemPrompt = document.getElementById('agent-system-prompt').value.trim();
    const description = document.getElementById('agent-description').value.trim();

    if (!name) {
        showToast('请输入 Agent 名称', 'error');
        return;
    }

    const data = {
        name,
        system_prompt: systemPrompt || 'You are a helpful assistant.',
        description: description || null,
    };

    showLoading();
    try {
        if (state.editingAgentId) {
            await api.updateAgent(state.editingAgentId, data);
            showToast('Agent 更新成功', 'success');
        } else {
            await api.createAgent(data);
            showToast('Agent 创建成功', 'success');
        }
        closeAgentModal();
        await loadAgents();
        
        // If editing current agent, refresh the display
        if (state.editingAgentId && state.currentAgent?.id === state.editingAgentId) {
            await selectAgent(state.editingAgentId);
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function deleteAgent() {
    if (!state.currentAgent) return;

    if (!confirm(`确定要删除 Agent "${state.currentAgent.name}" 吗？\n这将同时删除所有相关对话。`)) {
        return;
    }

    showLoading();
    try {
        await api.deleteAgent(state.currentAgent.id);
        showToast('Agent 删除成功', 'success');
        
        state.currentAgent = null;
        state.currentConversation = null;
        state.messages = [];
        
        document.getElementById('welcome-screen').style.display = 'flex';
        document.getElementById('chat-container').style.display = 'none';
        
        await loadAgents();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}


// =============================================================================
// Conversation Management (Requirements: 6.2)
// =============================================================================

function renderConversationList() {
    const container = document.getElementById('conversation-list');

    if (state.conversations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>暂无对话</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.conversations.map(conv => `
        <div class="conversation-item ${state.currentConversation?.id === conv.id ? 'active' : ''}"
             data-conversation-id="${conv.id}">
            <span class="conversation-item-title">${escapeHtml(conv.title || '新对话')}</span>
            <button class="conversation-item-delete" data-delete-id="${conv.id}" title="删除对话">×</button>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.classList.contains('conversation-item-delete')) {
                return;
            }
            const conversationId = parseInt(item.dataset.conversationId);
            selectConversation(conversationId);
        });
    });

    // Add delete handlers
    container.querySelectorAll('.conversation-item-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const conversationId = parseInt(btn.dataset.deleteId);
            await deleteConversation(conversationId);
        });
    });
}

async function loadConversations() {
    if (!state.currentAgent) return;

    try {
        const response = await api.getConversations(state.currentAgent.id);
        state.conversations = response.data || [];
        renderConversationList();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function selectConversation(conversationId) {
    const conversation = state.conversations.find(c => c.id === conversationId);
    if (!conversation) return;

    state.currentConversation = conversation;
    renderConversationList();
    await loadMessages();
    updateMessageInput();
}

async function createConversation() {
    if (!state.currentAgent) return;

    showLoading();
    try {
        const response = await api.createConversation(state.currentAgent.id, {});
        const newConversation = response.data;
        
        state.conversations.unshift(newConversation);
        state.currentConversation = newConversation;
        state.messages = [];
        
        renderConversationList();
        renderMessages();
        updateMessageInput();
        
        showToast('新对话已创建', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function deleteConversation(conversationId) {
    if (!confirm('确定要删除这个对话吗？')) {
        return;
    }

    showLoading();
    try {
        await api.deleteConversation(conversationId);
        
        state.conversations = state.conversations.filter(c => c.id !== conversationId);
        
        if (state.currentConversation?.id === conversationId) {
            state.currentConversation = null;
            state.messages = [];
            renderMessages();
            updateMessageInput();
        }
        
        renderConversationList();
        showToast('对话已删除', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}


// =============================================================================
// Message Display and Sending (Requirements: 6.3, 6.4)
// =============================================================================

function renderMessages() {
    const container = document.getElementById('messages-list');

    if (!state.currentConversation) {
        container.innerHTML = `
            <div class="empty-state">
                <p>👆 选择或创建一个对话开始聊天</p>
            </div>
        `;
        return;
    }

    if (state.messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>💬 开始新对话</p>
                <p>输入消息与 AI 交流</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.messages.map(msg => `
        <div class="message ${msg.role}">
            <div class="message-content">${escapeHtml(msg.content)}</div>
            <div class="message-time">${formatTime(msg.created_at)}</div>
        </div>
    `).join('');

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function loadMessages() {
    if (!state.currentConversation) return;

    try {
        const response = await api.getMessages(state.currentConversation.id);
        state.messages = response.data || [];
        renderMessages();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function updateMessageInput() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('btn-send');
    const hasConversation = state.currentConversation !== null;

    input.disabled = !hasConversation;
    sendBtn.disabled = !hasConversation;

    if (hasConversation) {
        input.placeholder = '输入消息...';
        input.focus();
    } else {
        input.placeholder = '请先选择或创建一个对话';
    }
}

function showTypingIndicator() {
    const container = document.getElementById('messages-list');
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendMessage(event) {
    event.preventDefault();

    const input = document.getElementById('message-input');
    const content = input.value.trim();

    if (!content || !state.currentConversation) return;

    // Clear input immediately
    input.value = '';
    input.style.height = 'auto';

    // Add user message to UI immediately
    const userMessage = {
        id: Date.now(),
        role: 'user',
        content: content,
        created_at: new Date().toISOString(),
    };
    state.messages.push(userMessage);
    renderMessages();

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await api.sendMessage(state.currentConversation.id, content);
        
        // Remove temporary user message and add real messages
        state.messages.pop();
        
        if (response.data.user_message) {
            state.messages.push(response.data.user_message);
        }
        if (response.data.assistant_message) {
            state.messages.push(response.data.assistant_message);
        }

        hideTypingIndicator();
        renderMessages();

        // Update conversation title if it's the first message
        if (state.messages.length <= 2) {
            await loadConversations();
        }
    } catch (error) {
        hideTypingIndicator();
        // Remove the temporary user message on error
        state.messages.pop();
        renderMessages();
        showToast(error.message, 'error');
    }
}

// Auto-resize textarea
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}


// =============================================================================
// Event Listeners and Initialization
// =============================================================================

function initializeEventListeners() {
    // Agent modal
    document.getElementById('btn-new-agent').addEventListener('click', () => openAgentModal());
    document.getElementById('btn-edit-agent').addEventListener('click', () => {
        if (state.currentAgent) {
            openAgentModal(state.currentAgent.id);
        }
    });
    document.getElementById('btn-delete-agent').addEventListener('click', deleteAgent);
    document.getElementById('modal-close').addEventListener('click', closeAgentModal);
    document.getElementById('btn-cancel').addEventListener('click', closeAgentModal);
    document.getElementById('agent-form').addEventListener('submit', saveAgent);

    // Close modal on outside click
    document.getElementById('agent-modal').addEventListener('click', (e) => {
        if (e.target.id === 'agent-modal') {
            closeAgentModal();
        }
    });

    // Conversation
    document.getElementById('btn-new-conversation').addEventListener('click', createConversation);

    // Message form
    document.getElementById('message-form').addEventListener('submit', sendMessage);

    // Auto-resize textarea
    const messageInput = document.getElementById('message-input');
    messageInput.addEventListener('input', () => autoResizeTextarea(messageInput));

    // Send on Enter (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('message-form').dispatchEvent(new Event('submit'));
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to close modal
        if (e.key === 'Escape') {
            closeAgentModal();
        }
        // Ctrl/Cmd + N for new agent
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            openAgentModal();
        }
    });
}

// Initialize application
async function init() {
    initializeEventListeners();
    showLoading();
    try {
        await loadAgents();
    } finally {
        hideLoading();
    }
}

// Start the application when DOM is ready
document.addEventListener('DOMContentLoaded', init);
