import { MqttClient } from 'mqtt';
import { connectionMessage } from './payload-builder';
import { pubOptions, subOptions } from './const/options';
import { root } from './const/topic-pattern';
import { InitialToken } from "./types";
// default server
const baseServerTopic = `${root.server}/1`;
// topic to send data
let dataTopic = '';

export const setupEventHandlers = (client: MqttClient): MqttClient => {
    const mqttProtocol = client.options.protocol;
    const connectionTopic = `${baseServerTopic}/connection`;
    const baseClientTopic = `${root.client}/${client.options.clientId}`;
    client.on('connect', () => {
        client.subscribe([`${baseClientTopic}/#`], subOptions, () => {
            console.log(`${mqttProtocol}: Subscribe to topic '${baseClientTopic}/#'`)
        });
        client.publish(connectionTopic, 
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
        if (topic === baseClientTopic)
        {
            console.log(payload.toString());
            let json: InitialToken = JSON.parse(payload.toString());
            dataTopic = `${baseServerTopic}/${json.token}`;
            setInterval(function() {
                client.publish(dataTopic, 
                    `data payload ${Math.random().toString(16).slice(3)}`, 
                    pubOptions, 
                    (error) => {
                         if (error) {
                             console.error(error);
                     }
                    });
            }, 5000);
        }
    });
    return client;
}