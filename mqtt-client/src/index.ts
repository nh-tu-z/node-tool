import figlet from 'figlet';
import chalk from 'chalk';
import mqtt from 'mqtt';
import { Command } from 'commander';
import { mqttOptions } from './options';
import { setupEventHandlers } from './event-handler';

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

console.log(connectUrl)
const client = mqtt.connect(connectUrl, mqttOptions);

setupEventHandlers(client);
