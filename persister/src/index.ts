import figlet from 'figlet';
import chalk from 'chalk';
import { Command } from 'commander';

console.log(chalk.green(figlet.textSync("Persister")));

const program = new Command();

program
  .version('1.0.0')
  .description('Persist data into Mongo collection')
  .option(  '-r, --protocol <type>', 'connect protocol: mqtt, mqtts, ws, wss. default is mqtt', 'mqtt')
  .option(  '-i, --ip <type>', 'host ip address', '0.0.0.0')
  .option(  '-p, --port <type>', 'port', '8883')
  .parse(process.argv);

const options = program.opts();