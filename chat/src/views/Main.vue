<template>
  <div class="main">
    <p>Welcome, {{ userData.username }}!</p>
    <button @click="logout">Logout</button>
  </div>
</template>

<script>
export default {
  computed: {
    userData() {
      return this.$store.state.userData;
    },
  },
  methods: {
    logout() {
      this.$store.commit("clearUserData");
      this.$router.push("/");
    },
  },
};
</script>
