import figlet from 'figlet';
import chalk from 'chalk';
import mqtt from 'mqtt';
import { Command } from 'commander';
import { mqttOptions } from './options';

console.log(chalk.green(figlet.textSync("MQTT Client")));

const program = new Command();

program
  .version('1.0.0')
  .description('MQTT Client Mock')
  .option(  '-r, --protocol <type>', 'connect protocol: mqtt, mqtts, ws, wss. default is mqtt', 'mqtt')
  .option(  '-i, --ip <type>', 'host ip address', '0.0.0.0')
  .option(  '-p, --port <type>', 'port', '8883')
  .parse(process.argv);

const options = program.opts();

const host = options.ip;
const port = options.port;

// accepted protocol list
const PROTOCOLS = ['mqtt', 'mqtts', 'ws', 'wss']

// default is mqtt, unencrypted tcp connection
let connectUrl = `mqtt://${host}:${port}`;
console.log(connectUrl)
if (options.protocol && PROTOCOLS.indexOf(options.protocol) === -1) {
    console.log('protocol must one of mqtt, mqtts, ws, wss.');
} 
else if (options.protocol === 'mqtts') {
    // mqtts， encrypted tcp connection
    connectUrl = `mqtts://${host}:8883`;
    //OPTIONS['ca'] = fs.readFileSync('./broker.emqx.io-ca.crt')
} 
else if (options.protocol === 'ws') {
    // ws, unencrypted WebSocket connection
    const mountPath = '/mqtt' // mount path, connect emqx via WebSocket
    connectUrl = `ws://${host}:8083${mountPath}`;
} 
else if (options.protocol === 'wss') {
    // wss, encrypted WebSocket connection
    const mountPath = '/mqtt' // mount path, connect emqx via WebSocket
    connectUrl = `wss://${host}:8084${mountPath}`;
    //OPTIONS['ca'] = fs.readFileSync('./broker.emqx.io-ca.crt')
} 

const topic = 'default-mqtt-topic';

const client = mqtt.connect(connectUrl, mqttOptions);

client.on('connect', () => {
    console.log(`${options.protocol}: Connected`)
    client.subscribe([topic], () => {
      console.log(`${options.protocol}: Subscribe to topic '${topic}'`)
    })
    client.publish(topic, 'nodejs mqtt test', { qos: 0, retain: false }, (error) => {
      if (error) {
        console.error(error)
      }
    })
})
  
client.on('reconnect', () => {
console.log(`Reconnecting(${program.options})`)
})

client.on('error', (error) => {
console.log(`Cannot connect(${program.options}):`, error)
})

client.on('message', (topic, payload) => {
console.log('Received Message:', topic, payload.toString())
})
