<template>
  <div class="register">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input type="text" v-model="username" placeholder="Username" />
      <input type="password" v-model="password" placeholder="Password" />
      <button type="submit">Register</button>
    </form>
    <p>Already have an account? <router-link to="/">Login</router-link></p>
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
    register() {
      socket.emit("register", { username: this.username, password: this.password });
      socket.on("register", (data) => {
        if (data.success) {
          this.$store.commit("setUserData", data.user);
          this.$store.commit("LogIn", true);
          this.$router.push("/main");
        } else {
          alert("Registration failed. Please try again.");
        }
      });
    },
  },
};
</script>
