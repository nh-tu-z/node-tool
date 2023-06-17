## Migratie

### 1. Overview
Migrate tool built based on [Evolve](https://evolve-db.netlify.app/)

### 2. Use cases
- Migrate sql script in 'migrate' mode in localhost (SQL Server):
    + Make sure SQL Server is already installed in local machine
    + Add arguments and start running in Visual Studio (debug mode):
    ```shell
    # arguments
    --connectionString Server=localhost;Database=sysb;Trusted_Connection=True; --location D:\Migratie\Migratie\Script\ --executeType migrate
    ```
    + Check the `changelog` table and result in the `SQL Client` such as `SSMS`

- Correct the checksum in 'repair' mode: ->> Not test yet