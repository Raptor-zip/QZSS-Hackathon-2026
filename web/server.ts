import express from 'express';
import type { Request, Response } from 'express';
import net from 'net';
import path from 'path';

const app = express();
const port = 3000;
const PYTHON_PORT = 65432;
const PYTHON_HOST = '127.0.0.1';

app.use(express.static('public'));
app.use(express.json());

interface Command {
    cmd: string;
    relay?: number;
    state?: boolean;
}

// Function to send command to Python
function sendToPython(command: Command): Promise<string> {
    return new Promise((resolve, reject) => {
        const client = new net.Socket();

        client.connect(PYTHON_PORT, PYTHON_HOST, () => {
            console.log('Connected to Python');
            client.write(JSON.stringify(command));
            client.end();
        });

        client.on('data', (data) => {
            console.log('Received from Python: ' + data.toString());
            client.destroy(); // kill client after server's response
            resolve(data.toString());
        });

        client.on('error', (err) => {
            console.error("Python Connection Error: " + err.message);
            client.destroy();
            reject(err);
        });
    });
}

// Toggle Endpoint (Legacy support if needed, or remove)
app.post('/api/toggle', (req: Request, res: Response) => {
    const relayId = req.body.relay;
    console.log(`Toggling Relay ${relayId}`);

    sendToPython({ cmd: 'toggle', relay: relayId });
    res.json({ success: true });
});

// Set State Endpoint
app.post('/api/relay', (req: Request, res: Response) => {
    const relayId = Number(req.body.relay);
    const state = Boolean(req.body.state);

    console.log(`Setting Relay ${relayId} to ${state ? 'ON' : 'OFF'}`);

    sendToPython({ cmd: 'set', relay: relayId, state: state });
    res.json({ success: true });
});

app.listen(port, () => {
    console.log(`Web Controller listening at http://0.0.0.0:${port}`);
});
