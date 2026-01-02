import express from 'express';
import { createServer } from 'http';
import { Server, Socket } from 'socket.io';
import path from 'path';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: { origin: "*" }
});

const port = 3000;

app.use(express.static('public'));
app.use(express.json());

// Relay Logic
io.on('connection', (socket: Socket) => {
    console.log('Client connected:', socket.id);

    // When Python client sends Status Update
    socket.on('s2c_status', (data) => {
        console.log('Relaxing status update to all clients:', data);
        // Broadcast to all web clients (and the python client itself, though unrelated)
        io.emit('s2c_status', data);
    });

    // When Web Client sends Control Command
    socket.on('c2s_control', (data) => {
        console.log('Control command received:', data);
        // Relay to Python listeners
        // We broadcast to everyone, Python client will hear it and act.
        io.emit('c2s_control', data);
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
    });
});


// Legacy API Support (Optional - redirects to socket emit)
app.post('/api/relay', (req, res) => {
    const relayId = req.body.relay;
    const state = req.body.state;
    console.log(`Legacy API: Setting Relay ${relayId} to ${state}`);
    io.emit('c2s_control', { cmd: 'set', relay: relayId, state: state });
    res.json({ success: true });
});

httpServer.listen(port, () => {
    console.log(`Socket.IO Server listening at http://0.0.0.0:${port}`);
});
