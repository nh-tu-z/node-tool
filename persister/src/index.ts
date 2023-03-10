import figlet from 'figlet';
import chalk from 'chalk';
import { Command } from 'commander';
import { connect } from 'mongoose';
import { schemaBuilder } from './schema/device-schema';
import { schemaName, errMsg } from './const';
import { dbOptions } from './config/configOptions';
import inputData from './input-data.json'

console.log(chalk.green(figlet.textSync("Persister")));

console.log(inputData)

const program = new Command();

let supportSchemas = [];
let item: keyof typeof schemaName
for (item in schemaName) {
    supportSchemas.push(schemaName[item]);
}

/*
Initial requirement:
Provide some options for user to choose (i.e. connection string, collection name, data input, v.v.) to store data.
TODO - The tool should be able to do a sanity check for specific collection.
TODO - Query data back as JSON format.
 */
program
  .version('1.0.0')
  .description('Persist data into Mongo collection')
  .option('-u, --uri <uri>', 'URI to connect to MongoDB', 'mongodb://127.0.0.1:27017')
  .requiredOption('-d, --db <name>', 'Database Name')
  .requiredOption('-c, --collection <name>', `Collection Name. It should be one of [${supportSchemas.join(', ')}]`)
  //
  .parse(process.argv);

const options = program.opts();

let dbPath = `${options.uri}/${options.db}`;
console.log(dbPath);

let targetSchema = schemaBuilder(options.collection);
console.log(targetSchema);
if (targetSchema !== errMsg.notSupportSchema) {
    async function run() {
        //await connect(dbPath);
        await connect(dbPath, dbOptions,
            (err) => {
              if (err) throw err;
              console.log('connect successfully')
            });
      
        // TODO - check type inputData before using

        const item = new targetSchema(inputData);
        await item.save();
        
        // TODO - how to exit after done
        console.log('done');
    }
    run().catch(err => console.log(err));
}
else {
    // terminate
    console.log('terminate')
}

