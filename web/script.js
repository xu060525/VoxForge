let isListening = true; // 前端也进行状态的记录

// 暴露给 Python 调用的函数
eel.expose(update_status);
function update_status(text, state) {
    document.getElementById("status-text").innerText = text;
    
    let circle = document.getElementById("status-indicator");
    circle.className = "circle"; // 重置
    if (state === "listening") circle.classList.add("listening");
    if (state === "processing") circle.classList.add("processing");
}

eel.expose(add_message);
function add_message(text, sender) {
    let box = document.getElementById("chat-box");
    let div = document.createElement("div");
    div.className = "message " + sender; // sender 是 'user' 或 'bot'
    div.innerText = (sender === 'user' ? "You: " : "VF: ") + text;
    box.appendChild(div);
    // 自动滚动到底部
    box.scrollTop = box.scrollHeight;
}

function toggleListening() {
    let btn = document.getElementById("toggle-btn");

    if(isListening) {
        // 暂停
        eel.set_listening_state(false); // 调用 Python
        btn.innerText = "开始";
        btn.style.backgroundColor = "#555";
        isListening = false;
        update_status("已暂停", "idle");
    } else {
        // 开始
        eel.set_listening_state(true);  // 调用 Python
        btn.innerText = "暂停";
        btn.style.backgroundColor = ""; // 恢复默认
        isListening = true;
        update_status("正在监听...", "listening");
    }
}