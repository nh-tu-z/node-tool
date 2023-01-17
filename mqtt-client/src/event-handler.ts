import { MqttClient } from 'mqtt';
import { connectionMessage } from './payload-builder';

const connectionGatewayTopic = 'connection-gateway/01';
const connectionSetupTopic = 'connection-setup/';

export const setupEventHandlers = (client: MqttClient): MqttClient => {
    const mqttProtocol = client.options.protocol;
    client.on('connect', () => {
        const setupTopic = `${connectionSetupTopic}${client.options.clientId}`;
        client.subscribe([setupTopic], () => {
            console.log(`${setupTopic}: Subscribe to topic '${setupTopic}'`)
        });
        client.publish(connectionGatewayTopic, connectionMessage(client.options.clientId as string), { qos: 0, retain: false }, (error) => {
            if (error) {
                console.error(error);
            }
        });

        client.on('message', (topic, message) => {
            console.log(topic, message.toString());
        });
    });

    client.on('reconnect', (error: string) => {
        console.log(`Reconnecting(${mqttProtocol}):`, error)
    });
      
    client.on('error', (error) => {
        console.log(`Cannot connect(${mqttProtocol}):`, error)
    });
      
    client.on('message', (topic, payload) => {
        console.log('Received Message:', topic, payload.toString())
    });
    return client;
}