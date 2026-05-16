const fastify = require('fastify')({ logger: false });

fastify.get('/io', async (request, reply) => {
    return { status: 'ok' };
});

fastify.post('/json', async (request, reply) => {
    const authHeader = request.headers['authorization'];
    
    if (authHeader !== 'Bearer secret-token') {
        const err = new Error('Unauthorized');
        err.statusCode = 401;
        throw err;
    }

    const now = Date.now();
    const items = request.body;
    
    const processed = items.map(item => ({
        id: item.id,
        name: item.name,
        processedAt: now
    }));

    return processed;
});

fastify.listen({ port: 3000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
});