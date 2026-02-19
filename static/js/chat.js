document.addEventListener("DOMContentLoaded", () => {
  let currentChatId = null;
  let isLoading = false;
  let currentLanguage = localStorage.getItem("language") || "en";
  let translations = {};

  if (!window.API || !window.formatDate) {
    console.error(
      "[Chatbot] Required dependencies (API, formatDate) not loaded. Please ensure main.js is loaded first.",
    );
    return;
  }

  // Load translations
  async function loadTranslations(lang) {
    try {
      const data = await window.API.get(`/chat/translations/${lang}`);
      translations = data.translations;
      updateUILanguage();
    } catch (error) {
      console.error("[Chatbot] Failed to load translations:", error);
    }
  }

  // Update UI with current language
  function updateUILanguage() {
    const t = translations;
    
    // Update text elements (skip university name - loaded separately)
    document.getElementById('newChatBtn').innerHTML = t.new_chat || '+ New Chat';
    document.getElementById('logoutBtn').textContent = t.logout || 'Logout';
    document.querySelector('.welcome-message h2').textContent = t.welcome_title || 'Welcome to Algerian Universities AI Assistant';
    document.querySelector('.welcome-message p').textContent = t.welcome_subtitle || 'How can I assist you today?';
    document.getElementById('messageInput').placeholder = t.type_message || 'Type your message here...';
    document.querySelector('.chat-input-form button span').textContent = t.send || 'Send';
    
    // Update settings
    if (document.querySelector('.settings-header h2')) {
      document.querySelector('.settings-header h2').textContent = t.settings_title || 'Settings';
    }

    // Set text direction for Arabic
    if (currentLanguage === 'ar') {
      document.body.setAttribute('dir', 'rtl');
      document.body.classList.add('rtl');
    } else {
      document.body.setAttribute('dir', 'ltr');
      document.body.classList.remove('rtl');
    }
  }

  // Load user info and university
  async function loadUserInfo() {
    try {
      const data = await window.API.get("/auth/me");
      const userInfoDiv = document.getElementById("userInfo");
      userInfoDiv.textContent = data.user.username;
      
      // Load and display university name
      if (data.user.university_id) {
        try {
          const universitiesData = await window.API.get("/auth/universities");
          const university = universitiesData.universities.find(u => u.id === data.user.university_id);
          if (university) {
            const universityNameDiv = document.getElementById("universityName");
            if (universityNameDiv) {
              universityNameDiv.textContent = university.name;
            }
          }
        } catch (error) {
          console.error("[Chatbot] Failed to load university:", error);
        }
      }
    } catch (error) {
      console.error("[Chatbot] Failed to load user info:", error);
    }
  }

  // Load chat list
  async function loadChatList() {
    try {
      const data = await window.API.get("/chat/list");
      const chatList = document.getElementById("chatList");

      if (data.chats.length === 0) {
        chatList.innerHTML = `<p style="padding: 12px; color: var(--text-secondary); font-size: 14px;">${translations.no_chats || 'No chats yet'}</p>`;
        return;
      }

      chatList.innerHTML = data.chats
        .map(
          (chat) => `
            <div class="chat-item" data-chat-id="${chat.id}" data-updated-at="${chat.updated_at}">
                <div class="chat-item-title">${chat.title}</div>
                <div class="chat-item-time">${window.formatDate(chat.updated_at)}</div>
            </div>
        `,
        )
        .join("");

      // Add click handlers
      document.querySelectorAll(".chat-item").forEach((item) => {
        item.addEventListener("click", () => {
          const chatId = Number.parseInt(item.dataset.chatId);
          loadChat(chatId);
        });
      });
    } catch (error) {
      console.error("[Chatbot] Failed to load chats:", error);
    }
  }

  // Refresh timestamps in chat list every minute
  function refreshTimestamps() {
    document.querySelectorAll(".chat-item").forEach((item) => {
      const updatedAt = item.dataset.updatedAt;
      if (updatedAt) {
        const timeElement = item.querySelector('.chat-item-time');
        if (timeElement) {
          timeElement.textContent = window.formatDate(updatedAt);
        }
      }
    });
  }

  // Set up timestamp refresh interval (every 60 seconds)
  setInterval(refreshTimestamps, 60000);

  // Format message content (supports markdown-style formatting)
  function formatMessageContent(content) {
    // Convert **bold** to <strong>
    content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    content = content.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Convert newlines to <br>
    content = content.replace(/\n/g, '<br>');
    
    // Convert code blocks ```code``` to <pre><code>
    content = content.replace(/```(\w+)?\n?([\s\S]+?)```/g, (match, lang, code) => {
      return `<pre><code class="language-${lang || 'plaintext'}">${escapeHtml(code.trim())}</code></pre>`;
    });
    
    // Convert inline code `code` to <code>
    content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert URLs to links
    content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    
    return content;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Create message HTML with actions
  function createMessageHTML(msg, showActions = true) {
    const formattedContent = formatMessageContent(msg.content);
    const actionsHTML = showActions && msg.role === 'assistant' ? `
      <div class="message-actions">
        <button class="message-action-btn copy-btn" data-content="${escapeHtml(msg.content)}" title="${translations.copy || 'Copy'}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
        <button class="message-action-btn regenerate-btn" data-message-id="${msg.id}" title="${translations.regenerate || 'Regenerate'}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
      </div>
    ` : '';

    return `
      <div class="message ${msg.role}" data-message-id="${msg.id}">
        <div class="message-content">${formattedContent}</div>
        ${actionsHTML}
      </div>
    `;
  }

  // Load specific chat
  async function loadChat(chatId) {
    try {
      const data = await window.API.get(`/chat/${chatId}`);
      currentChatId = chatId;

      // Update UI
      document.getElementById("chatTitle").textContent = data.chat.title;

      // Enable input
      document.getElementById("messageInput").disabled = false;
      document.querySelector(".chat-input-form button").disabled = false;

      // Display messages
      const messagesDiv = document.getElementById("chatMessages");
      messagesDiv.innerHTML = data.messages
        .map(msg => createMessageHTML(msg))
        .join("");

      // Add event listeners to message actions
      attachMessageActionListeners();

      // Apply code highlighting if enabled
      if (localStorage.getItem('codeHighlight') !== 'false') {
        highlightCode();
      }

      messagesDiv.scrollTop = messagesDiv.scrollHeight;

      // Update active state
      document.querySelectorAll(".chat-item").forEach((item) => {
        item.classList.toggle(
          "active",
          Number.parseInt(item.dataset.chatId) === chatId,
        );
      });
    } catch (error) {
      console.error("[Chatbot] Failed to load chat:", error);
    }
  }

  // Highlight code blocks
  function highlightCode() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
      block.classList.add('highlighted');
    });
  }

  // Attach event listeners to message action buttons
  function attachMessageActionListeners() {
    // Copy buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const content = btn.dataset.content;
        try {
          await navigator.clipboard.writeText(content);
          const originalHTML = btn.innerHTML;
          btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>`;
          btn.classList.add('success');
          setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.classList.remove('success');
          }, 2000);
        } catch (error) {
          console.error('[Chatbot] Failed to copy:', error);
        }
      });
    });

    // Regenerate buttons
    document.querySelectorAll('.regenerate-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const messageId = btn.dataset.messageId;
        await regenerateMessage(messageId);
      });
    });
  }

  // Regenerate message
  async function regenerateMessage(messageId) {
    if (!currentChatId || isLoading) return;

    isLoading = true;
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    
    if (!messageElement) return;

    // Show loading state
    const originalContent = messageElement.querySelector('.message-content').innerHTML;
    messageElement.querySelector('.message-content').innerHTML = `
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
    `;

    try {
      const data = await window.API.post(`/chat/${currentChatId}/message/${messageId}/regenerate`);
      
      // Update message
      messageElement.querySelector('.message-content').innerHTML = formatMessageContent(data.message.content);
      
      // Re-attach action listeners
      attachMessageActionListeners();
      
      // Apply code highlighting
      if (localStorage.getItem('codeHighlight') !== 'false') {
        highlightCode();
      }
    } catch (error) {
      console.error('[Chatbot] Failed to regenerate:', error);
      messageElement.querySelector('.message-content').innerHTML = originalContent;
    } finally {
      isLoading = false;
    }
  }

  // Create new chat
  async function createNewChat() {
    try {
      const data = await window.API.post("/chat/new", {
        title: translations.new_conversation || "New Conversation",
      });
      await loadChatList();
      loadChat(data.chat.id);
    } catch (error) {
      console.error("[Chatbot] Failed to create chat:", error);
    }
  }

  // Send message
  async function sendMessage(message) {
    if (!currentChatId || isLoading) return;

    isLoading = true;
    const messagesDiv = document.getElementById("chatMessages");
    const messageInput = document.getElementById("messageInput");

    // Check if this is the first message
    const existingMessages = messagesDiv.querySelectorAll(".message");
    const isFirstMessage = existingMessages.length === 0;

    // Display user message
    const userMsgHTML = createMessageHTML({role: 'user', content: message}, false);
    messagesDiv.innerHTML += userMsgHTML;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Show loading
    messagesDiv.innerHTML += `
        <div class="message assistant loading">
            <div class="message-content">
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    messageInput.value = "";

    try {
      const data = await window.API.post(`/chat/${currentChatId}/message`, {
        message,
        use_faq: true
      });

      // Remove loading
      document.querySelector(".message.loading")?.remove();

      // Display AI response with FAQ badge if applicable
      let responseContent = data.ai_message.content;
      if (data.faq_match) {
        const faqBadge = `<div class="faq-badge">${translations.faq_match || 'From FAQ'} (${Math.round(data.faq_match.confidence * 100)}%)</div>`;
        responseContent = faqBadge + responseContent;
      }

      const aiMsgHTML = createMessageHTML({
        id: data.ai_message.id,
        role: 'assistant',
        content: responseContent
      });
      messagesDiv.innerHTML += aiMsgHTML;
      
      // Attach action listeners
      attachMessageActionListeners();
      
      // Apply code highlighting
      if (localStorage.getItem('codeHighlight') !== 'false') {
        highlightCode();
      }

      messagesDiv.scrollTop = messagesDiv.scrollHeight;

      // Update title if this was the first message
      if (isFirstMessage && data.chat_title) {
        document.getElementById("chatTitle").textContent = data.chat_title;
      }

      // Reload chat list to update timestamps and titles
      await loadChatList();
    } catch (error) {
      console.error("[Chatbot] Failed to send message:", error);
      document.querySelector(".message.loading")?.remove();
      messagesDiv.innerHTML += `
            <div class="message assistant">
                <div class="message-content" style="color: var(--error);">${translations.failed_response || 'Failed to get response. Please try again.'}</div>
            </div>
        `;
    } finally {
      isLoading = false;
    }
  }

  // Event listeners
  document
    .getElementById("newChatBtn")
    .addEventListener("click", createNewChat);

  document.getElementById("messageForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("messageInput");
    const message = input.value.trim();
    if (message) {
      sendMessage(message);
    }
  });

  // Add keyboard shortcut for sending (Ctrl+Enter or Cmd+Enter)
  document.getElementById("messageInput").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      const message = e.target.value.trim();
      if (message) {
        sendMessage(message);
      }
    }
  });

  document.getElementById("logoutBtn").addEventListener("click", async () => {
    try {
      await window.API.post("/auth/logout");
      window.location.href = "/auth/login";
    } catch (error) {
      console.error("[Chatbot] Logout failed:", error);
    }
  });

  // Settings panel functionality
  const settingsBtn = document.getElementById("settingsBtn");
  const settingsPanel = document.getElementById("settingsPanel");
  const closeSettings = document.getElementById("closeSettings");
  const settingsOverlay = settingsPanel?.querySelector(".settings-overlay");

  if (settingsBtn && settingsPanel && closeSettings && settingsOverlay) {
    settingsBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      settingsPanel.classList.add("active");
      loadSettingsData();
    });

    closeSettings.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      settingsPanel.classList.remove("active");
    });

    settingsOverlay.addEventListener("click", (e) => {
      e.stopPropagation();
      settingsPanel.classList.remove("active");
    });
  }

  // Load settings data
  async function loadSettingsData() {
    try {
      const data = await window.API.get("/auth/me");
      const profileName = document.getElementById("profileName");
      const profileEmail = document.getElementById("profileEmail");
      const profileDepartment = document.getElementById("profileDepartment");

      if (profileName) profileName.value = data.user.full_name || "";
      if (profileEmail) profileEmail.value = data.user.email || "";
      if (profileDepartment)
        profileDepartment.value = data.user.department || "";
    } catch (error) {
      console.error("[Chatbot] Failed to load settings:", error);
    }
  }

  // Save profile
  const saveProfileBtn = document.getElementById("saveProfile");
  if (saveProfileBtn) {
    saveProfileBtn.addEventListener("click", async () => {
      const name = document.getElementById("profileName")?.value;
      const department = document.getElementById("profileDepartment")?.value;

      try {
        await window.API.post("/auth/update-profile", {
          full_name: name,
          department: department,
        });
        alert(translations.profile_updated || "Profile updated successfully!");
      } catch (error) {
        console.error("[Chatbot] Failed to save profile:", error);
        alert(translations.profile_update_failed || "Failed to update profile. Please try again.");
      }
    });
  }

  // Theme switching
  const themeOptions = document.querySelectorAll(".theme-option");
  if (themeOptions.length > 0) {
    themeOptions.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        themeOptions.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        const theme = btn.dataset.theme;

        if (theme === "light") {
          document.body.classList.add("light-theme");
        } else {
          document.body.classList.remove("light-theme");
        }

        localStorage.setItem("theme", theme);
      });
    });
  }

  // Load saved theme
  const savedTheme = localStorage.getItem("theme") || "dark";
  if (savedTheme === "light") {
    document.body.classList.add("light-theme");
    const lightBtn = document.querySelector('[data-theme="light"]');
    const darkBtn = document.querySelector('[data-theme="dark"]');
    if (lightBtn) lightBtn.classList.add("active");
    if (darkBtn) darkBtn.classList.remove("active");
  } else {
    document.body.classList.remove("light-theme");
    const darkBtn = document.querySelector('[data-theme="dark"]');
    const lightBtn = document.querySelector('[data-theme="light"]');
    if (darkBtn) darkBtn.classList.add("active");
    if (lightBtn) lightBtn.classList.remove("active");
  }

  // Font size
  const fontSizeSelect = document.getElementById("fontSize");
  if (fontSizeSelect) {
    fontSizeSelect.addEventListener("change", (e) => {
      const size = e.target.value;
      document.body.classList.remove("font-small", "font-medium", "font-large");
      document.body.classList.add(`font-${size}`);
      localStorage.setItem("fontSize", size);
    });

    const savedFontSize = localStorage.getItem("fontSize") || "medium";
    fontSizeSelect.value = savedFontSize;
    document.body.classList.remove("font-small", "font-medium", "font-large");
    document.body.classList.add(`font-${savedFontSize}`);
  }

  // Language switching
  const languageSelect = document.getElementById("language");
  if (languageSelect) {
    languageSelect.addEventListener("change", async (e) => {
      const language = e.target.value;
      currentLanguage = language;
      localStorage.setItem("language", language);
      
      // Load new translations and update UI
      await loadTranslations(language);
      
      // Reload chat list to show updated text
      await loadChatList();
    });

    const savedLanguage = localStorage.getItem("language") || "en";
    languageSelect.value = savedLanguage;
    currentLanguage = savedLanguage;
  }

  // Creativity slider
  const creativitySlider = document.getElementById("creativity");
  const creativityValue = document.getElementById("creativityValue");

  if (creativitySlider && creativityValue) {
    creativitySlider.addEventListener("input", (e) => {
      const value = e.target.value;
      creativityValue.textContent = `${value}%`;
      localStorage.setItem("creativity", value);
    });

    const savedCreativity = localStorage.getItem("creativity") || "70";
    creativitySlider.value = savedCreativity;
    creativityValue.textContent = `${savedCreativity}%`;
  }

  // Response style
  const responseStyleSelect = document.getElementById("responseStyle");
  if (responseStyleSelect) {
    responseStyleSelect.addEventListener("change", (e) => {
      const style = e.target.value;
      localStorage.setItem("responseStyle", style);
    });

    const savedResponseStyle =
      localStorage.getItem("responseStyle") || "balanced";
    responseStyleSelect.value = savedResponseStyle;
  }

  // Toggle switches
  const toggles = ["codeHighlight", "autoSave", "dataCollection"];
  toggles.forEach((id) => {
    const toggle = document.getElementById(id);
    if (toggle) {
      const saved = localStorage.getItem(id);
      if (saved !== null) {
        toggle.checked = saved === "true";
      }

      toggle.addEventListener("change", (e) => {
        const checked = e.target.checked;
        localStorage.setItem(id, checked);
      });
    }
  });

  // Export data
  const exportDataBtn = document.getElementById("exportData");
  if (exportDataBtn) {
    exportDataBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        const data = await window.API.get("/chat/export");
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `batna-university-chat-history-${new Date().toISOString()}.json`;
        link.click();
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error("[Chatbot] Failed to export data:", error);
        alert("Failed to export data. Please try again.");
      }
    });
  }

  // Clear history
  const clearHistoryBtn = document.getElementById("clearHistory");
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      if (confirm(translations.confirm_clear || "Are you sure you want to delete all chat history? This action cannot be undone.")) {
        try {
          await window.API.delete("/chat/clear-all");
          alert(translations.chats_cleared || "All chats have been deleted.");
          window.location.reload();
        } catch (error) {
          console.error("[Chatbot] Failed to clear history:", error);
          alert(translations.clear_failed || "Failed to clear history. Please try again.");
        }
      }
    });
  }

  // Initialize
  async function initialize() {
    await loadTranslations(currentLanguage);
    await loadUserInfo();
    await loadChatList();
    console.log("Batna University Chatbot initialized");
  }

  initialize();
});

