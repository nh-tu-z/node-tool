import { IClientOptions, IClientPublishOptions, IClientSubscribeOptions } from 'mqtt';

const clientId = `device_${Math.random().toString(16).slice(3)}`;

export const mqttOptions: IClientOptions = {
    clientId: clientId,
    connectTimeout: 4000,
    username: 'emqx',
    password: 'public',
    reconnectPeriod: 1000,
    // protocolId: 'MQIsdp',
    // protocolVersion: 3
};

export const pubOptions: IClientPublishOptions = {
    qos: 0, 
    retain: false
}

export const subOptions: IClientSubscribeOptions = {
    qos: 0
}