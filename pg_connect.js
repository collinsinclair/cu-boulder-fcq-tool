const pg = require('pg')
const connectionString = "postgres://postgres:pwd@localhost/fcq_tool";
const pgClient = new pg.Client(connectionString);

async function getRows() {
    await pgClient.connect();
    const res = await pgClient.query("SELECT * FROM \"FCQResultsRaw\" LIMIT 100;");
    res.rows.forEach(row => {
        console.log(row);
    });
    await pgClient.end();
}

getRows()