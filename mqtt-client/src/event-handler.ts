import { MqttClient } from 'mqtt';
import { connectionMessage } from './payload-builder';
import { pubOptions, subOptions } from './options';

const connectionGatewayTopic = 'connection-gateway/01';
const connectionSetupTopic = 'connection-setup/';

export const setupEventHandlers = (client: MqttClient): MqttClient => {
    const mqttProtocol = client.options.protocol;
    const setupTopic = `${connectionSetupTopic}${client.options.clientId}`;
    client.on('connect', () => {
        client.subscribe([setupTopic], subOptions, () => {
            console.log(`${setupTopic}: Subscribe to topic '${setupTopic}'`)
        });
        client.publish(connectionGatewayTopic, 
                       connectionMessage(client.options.clientId as string), 
                       pubOptions, 
                       (error) => {
                            if (error) {
                                console.error(error);
                        }
        });
    });

    client.on('reconnect', (error: string) => {
        console.log(`Reconnecting(${mqttProtocol}):`, error)
    });
      
    client.on('error', (error) => {
        console.log(`Cannot connect(${mqttProtocol}):`, error)
    });
      
    client.on('message', (topic, payload, packet) => {
        console.log('Received Message:', topic, payload.toString());
        if (topic === setupTopic)
        {
            
        }
    });
    return client;
}