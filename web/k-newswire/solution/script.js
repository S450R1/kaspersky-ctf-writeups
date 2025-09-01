let script = document.createElement('script');
script.src = 'https://cdn.socket.io/4.7.5/socket.io.min.js';
script.onload = function() {
  const socket = io('/', { path: '/socket.io', transports: ['websocket'] });
  socket.emit('join', { room: 'secret_announcements' });
  socket.on('news', (msg) => console.log(msg));
  socket.on('news_backlog', (msg) => console.log(msg));
};
document.head.appendChild(script);