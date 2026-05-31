const API_URL = '/ask';
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const welcome = document.getElementById('welcome');

let isLoading = false;

function handleSubmit(e) {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text || isLoading) return;
    sendMessage(text);
    userInput.value = '';
}

function askTopic(topic) {
    if (isLoading) return;
    sendMessage(topic);
}

async function sendMessage(text) {
    if (welcome) welcome.classList.add('hidden');
    addMessage('user', text);

    isLoading = true;
    sendBtn.disabled = true;

    // Show typing indicator
    const typingEl = showTyping();

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();

        typingEl.remove();

        if (res.ok) {
            addMessage('assistant', data.reply);
        } else {
            addMessage('assistant', 'Sorry, something went wrong. Please try again.');
        }
    } catch (err) {
        typingEl.remove();
        addMessage('assistant', 'Cannot connect to server. Please try again later.');
    }

    isLoading = false;
    sendBtn.disabled = false;
    userInput.focus();
}

function addMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `
        <div class="message-bubble">
            <p>${formatText(content)}</p>
            <span class="message-time">${getTime()}</span>
        </div>
    `;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTyping() {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = `
        <div class="message-bubble">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return div;
}

function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatText(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/#{1,6}\s*/g, '')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/- (.*?)(<br>|$)/g, '• $1$2');
}

function clearChat() {
    messagesContainer.innerHTML = '';
    if (welcome) {
        welcome.classList.remove('hidden');
        messagesContainer.appendChild(welcome);
    }
}

userInput.focus();
