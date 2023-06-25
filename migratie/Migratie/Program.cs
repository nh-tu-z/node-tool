using EvolveDb;
using Dapper;
using System;
using System.Data.SqlClient;
using System.Linq;

namespace Migratie
{
    internal class Program
    {
        private static string _connectionString = string.Empty;
        private static string _location = string.Empty;
        private static string _executeCommandType = string.Empty;
        /// <summary>
        /// Migrate the sql script
        /// </summary>
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                ShowHelp();
                return;
            }

            if (!ParseCommand(args))
                return;

            // FACT - Server=localhost;Database=scale;Trusted_Connection=True;
            var databaseName = _connectionString.Split(';')[1].Split('=')[1];
            CreateDatabaseIfAny(databaseName);

            Migrate(_executeCommandType);
            Console.ReadLine();
        }

        private static bool ParseCommand(string[] args)
        {
            if (args.Contains(Arguments.ConnectionString))
            {
                var index = Array.IndexOf(args, Arguments.ConnectionString);
                _connectionString = !args[index + 1].Contains("--") ? args[index + 1] : string.Empty;
            }

            if (args.Contains(Arguments.Location))
            {
                var index = Array.IndexOf(args, Arguments.Location);
                _location = !args[index + 1].Contains("--") ? args[index + 1] : string.Empty;
            }

            if (args.Contains(Arguments.ExecuteType))
            {
                var index = Array.IndexOf(args, Arguments.ExecuteType);
                _executeCommandType = !args[index + 1].Contains("--") ? args[index + 1] : string.Empty;
            }

            if (string.IsNullOrEmpty(_connectionString) ||
                string.IsNullOrEmpty(_location) ||
                string.IsNullOrEmpty(_executeCommandType))
            {
                return ShowHelp();
            }
            return true;
        }

        private static bool ShowHelp()
        {
            // TODO - apply StringBuilder
            var help = @"Migratie tool arguments:
                --connectionString: connection string of database that will be migrated
                --location: migrate location script
                --executeType: migrate | repair
            ";
            Console.WriteLine(help);
            return false;
        }

        private static void Migrate(string executeCommandType)
        {
            try
            {
                var connection = new SqlConnection(_connectionString);
                var evolve = new Evolve(connection, msg => Console.WriteLine(msg))
                {
                    Locations = new[] { _location },
                    IsEraseDisabled = true
                };

                Console.WriteLine($"Start migrating in '{executeCommandType}' mode...");
                if (executeCommandType == "migrate")
                {
                    evolve.Migrate();
                }
                else if (executeCommandType == "repair")
                {
                    evolve.Repair();
                }
                Console.WriteLine("Migrate done.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Database migration failed. {ex.Message}");
            }
        }

        // FACT - local dabase only
        private static void CreateDatabaseIfAny(string databaseName)
        {
            try
            {
                var connectionString = string.Format(Constants.ConnectionStringPattern, "localhost", "master");
                using (var connection = new SqlConnection(connectionString))
                {
                    connection.Open();

                    var databases = connection.Query<string>(Command.GetDatabaseNames).ToList();
                    if (!databases.Any(d => d == databaseName))
                    {
                        Console.WriteLine($"Create database [{databaseName}]...");
                        connection.Execute($"CREATE DATABASE [{databaseName}]");
                    }
                    Console.WriteLine($"[{databaseName}] created.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to create [{databaseName}].");
            }
        }
    }
}
