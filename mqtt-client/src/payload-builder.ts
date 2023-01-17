export function connectionMessage(clientId: string): string {
    let payload = {
        clientId
    };
    return JSON.stringify(payload);
}