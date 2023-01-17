import { IClientOptions } from 'mqtt';

const clientId = `mqtt_${Math.random().toString(16).slice(3)}`;

export const mqttOptions: IClientOptions = {
    clientId: clientId,
    connectTimeout: 4000,
    username: 'emqx',
    password: 'public',
    reconnectPeriod: 1000,
};