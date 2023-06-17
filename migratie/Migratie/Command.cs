using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Migratie
{
    public class Command
    {
        public const string GetDatabaseNames = @"SELECT * FROM sys.databases";
    }
}
