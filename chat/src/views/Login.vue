<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input type="text" v-model="username" placeholder="Username" />
      <input type="password" v-model="password" placeholder="Password" />
      <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <router-link to="/register">Register</router-link></p>
  </div>
</template>

<script>
import socket from "../socket";
export default {
  data() {
    return {
      username: "",
      password: "",
    };
  },
  methods: {
    login() {
      socket.emit("login", { username: this.username, password: this.password });
      socket.on("login", (data) => {
        if (data.error) {
          alert(data.error);
        } else {
          this.$store.commit("setUserData", data.user);
          this.$store.commit("LogIn", true);
          this.$router.push("/main");
        }
      });
    },
  },
};
</script>
