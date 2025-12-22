const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chips = document.querySelectorAll(".chip");

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(text, role, timestamp = new Date()) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;

  const body = document.createElement("div");
  body.className = "msg-body";
  body.textContent = text;

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.textContent = formatTime(timestamp);

  div.append(body, meta);
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}

async function sendMessage(message) {
  addMessage(message, "user");
  const thinkingEl = addMessage("Thinking...", "bot");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }

    const data = await res.json();
    const body = thinkingEl.querySelector(".msg-body");
    const meta = thinkingEl.querySelector(".msg-meta");
    if (body) {
      body.textContent = data.reply ?? "No response received.";
    }
    if (meta) {
      meta.textContent = formatTime(new Date());
    }
  } catch (err) {
    const body = thinkingEl.querySelector(".msg-body");
    if (body) {
      body.textContent = "Sorry, something went wrong. Please try again.";
    }
    console.error(err);
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  sendMessage(message);
});

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    chatInput.value = chip.dataset.prompt;
    chatInput.focus();
  });
});

// Seed a friendly greeting.
addMessage("Hi! Ask about Dakota's experience, projects, or skills.", "bot");

