## Persister

### 1. Overview
Persistence tool to check connection of specific collection and then introduce a way to store data

### 2. Use case
- Add a new record into specific collection:
    + We need to specify the data record in `input-data.json` manually as the same of the schema.
    + Run the command:
    ```shell
    # for example
    persister -d test -c Device
    ```
    + Check the result in the `Mongo` compass
