using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Migratie
{
    public class Constants
    {
        public const string ConnectionStringPattern = @"Server={0};Database={1};Trusted_Connection=True;";
    }

    public class Arguments
    {
        public const string ConnectionString = "--connectionString";
        public const string Location = "--location";
        public const string ExecuteType = "--executeType";
    }
}
