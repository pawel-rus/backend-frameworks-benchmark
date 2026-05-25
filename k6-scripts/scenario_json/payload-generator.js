export function generatePayload(targetKB) {

    const targetBytes = targetKB * 1024;

    const items = [];

    let counter = 0;

    while (true) {

        const item = {
            id: counter,
            name: 'x'.repeat(100),
            quantity: counter
        };

        items.push(item);

        const json = JSON.stringify(items);

        if (json.length >= targetBytes) {
            return json;
        }

        counter++;
    }
}