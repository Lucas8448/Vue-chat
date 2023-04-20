import io from 'socket.io-client'

const socket = io("http://127.0.0.1:3001/", {
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

export default socket
