let ws;

            function connectWebSocket() {
                const chatId = document.getElementById("chat_id").value;
                const userId = document.getElementById("user_id").value;
                if (!userId) {
                    alert("Please enter a User ID");
                    return;
                }
                ws = new WebSocket(`ws://localhost:8000/ws/${chatId}?user_id=${userId}`);
                document.getElementById("connected_chat").innerText = chatId;
                
                ws.onopen = function() {
                    document.getElementById("connection_status").innerText = "Connected successfully!";
                };

                ws.onmessage = function(event) {
                    const messagesContainer = document.getElementById("messages_container");
                    const newMessage = document.createElement("li");
                    newMessage.textContent = event.data;
                    messagesContainer.appendChild(newMessage);
                };
            }

            function sendMessage(event) {
                event.preventDefault();
                const messageInput = document.getElementById("message_input");
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(messageInput.value);
            
                    
                    messageInput.value = "";
                } else {
                    alert("WebSocket is not connected!");
                }
            }