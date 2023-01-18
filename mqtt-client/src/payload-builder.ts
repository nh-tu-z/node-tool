import { ConnectionMessagePayload } from "./types";

export function connectionMessage(clientId: string): string {
    let payload: ConnectionMessagePayload = {
        clientId
    };
    return JSON.stringify(payload);
}