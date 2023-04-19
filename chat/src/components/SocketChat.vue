<template>
  <div>
    <h2>Connected Users:</h2>
    <ul>
      <li v-for="user in connectedUsers" :key="user">{{ user }}</li>
    </ul>

    <h2>Messages:</h2>
    <ul>
      <li v-for="message in messages" :key="message.id">{{ message.text }}</li>
    </ul>

    <form @submit.prevent="sendMessage">
      <input type="text" v-model="newMessage" placeholder="Type your message..." />
      <button type="submit">Send</button>
    </form>
  </div>
</template>

<script>
import { io } from "socket.io-client";

export default {
  data() {
    return {
      connectedUsers: [],
      messages: [],
      newMessage: "",
    };
  },
  mounted() {
    var socket = io("http://127.0.0.1:3001/", {
      transportOptions: {
        polling: {
          extraHeaders: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS",
            "Access-Control-Allow-Headers":
              "Content-Type, Authorization, Content-Length, X-Requested-With",
          },
        },
      },
    });

    socket.on("connectedUsers", (users) => {
      this.connectedUsers = users;
    });

    socket.on("message", (message) => {
      this.messages.push(message);
    });
  },
  methods: {
    sendMessage() {
      const socket = io("http://localhost:3001");

      socket.emit("message", { text: this.newMessage });

      this.newMessage = "";
    },
  },
};
</script>
