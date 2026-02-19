// Utility Functions
window.API = {
  async request(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || "Request failed")
    }

    return data
  },

  get(url) {
    return this.request(url)
  },

  post(url, data) {
    return this.request(url, {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  put(url, data) {
    return this.request(url, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  },

  delete(url) {
    return this.request(url, {
      method: "DELETE",
    })
  },
}

// Date Formatting - Fixed to show accurate relative times
window.formatDate = function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  
  // Calculate difference in milliseconds
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  // Just now (less than 1 minute)
  if (diffMins < 1) return "just now"
  
  // Minutes ago (1-59 minutes)
  if (diffMins < 60) return `${diffMins} min ago`
  
  // Hours ago (1-23 hours)
  if (diffHours < 24) return `${diffHours}h ago`
  
  // Days ago (1-6 days)
  if (diffDays === 1) return "yesterday"
  if (diffDays < 7) return `${diffDays} days ago`
  
  // Weeks ago (7-27 days)
  if (diffDays < 28) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks} week${weeks > 1 ? 's' : ''} ago`
  }

  // Full date for older messages
  return date.toLocaleDateString()
}

// Show Notification
window.showNotification = function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.textContent = message
  document.body.appendChild(notification)

  setTimeout(() => {
    notification.remove()
  }, 3000)
}
