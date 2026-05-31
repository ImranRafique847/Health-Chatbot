const API_URL = '/ask/stream';
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
    // Hide welcome
    if (welcome) welcome.classList.add('hidden');

    // Add user message
    addMessage('user', text);

    // Create assistant bubble for streaming
    isLoading = true;
    sendBtn.disabled = true;

    const assistantDiv = document.createElement('div');
    assistantDiv.className = 'message assistant';
    assistantDiv.innerHTML = `
        <div class="message-bubble">
            <p class="stream-text"><span class="cursor">|</span></p>
            <span class="message-time">${getTime()}</span>
        </div>
    `;
    messagesContainer.appendChild(assistantDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    const streamText = assistantDiv.querySelector('.stream-text');
    let fullText = '';

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);

                    if (data === '[DONE]') break;

                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.text) {
                            fullText += parsed.text;
                            streamText.innerHTML = formatText(fullText) + '<span class="cursor">|</span>';
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        }
                        if (parsed.error) {
                            fullText = 'Sorry, an error occurred: ' + parsed.error;
                            streamText.innerHTML = fullText;
                        }
                    } catch (e) {}
                }
            }
        }
    } catch (err) {
        fullText = 'Cannot connect to server. Make sure the backend is running.';
    }

    // Remove cursor after streaming is done
    streamText.innerHTML = formatText(fullText);

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
