const fastify = require('fastify')({
    logger: false
});

/**
 * Scenario 1
 * Minimal routing benchmark
 */
fastify.get('/io', async (request, reply) => {
    return 'OKAY';
});

/**
 * Scenario 2
 * JSON serialization/deserialization benchmark
 */
fastify.post('/json', async (request, reply) => {

    const items = request.body;

    const processed = items.map(item => ({
        id: item.id,
        name: item.name.toUpperCase(),
        quantity: item.quantity + 1
    }));

    return processed;
});

/**
 * Scenario 3
 * Exception handling benchmark
 */
fastify.post('/exceptions', async (request, reply) => {

    const authorization = request.headers['authorization'];

    if (authorization !== 'Bearer secret-token') {

        const err = new Error(
            'Unauthorized access to endpoint. Either no, or invalid bearer token provided'
        );

        err.statusCode = 401;

        throw err;
    }

    return 'OKAY';
});

/**
 * Start server
 */
const start = async () => {

    try {

        await fastify.listen({
            port: 3000,
            host: '0.0.0.0'
        });

    } catch (err) {

        console.error(err);
        process.exit(1);
    }
};

start();