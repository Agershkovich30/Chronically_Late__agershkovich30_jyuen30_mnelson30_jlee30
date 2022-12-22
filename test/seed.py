import sqlite3
file_name = "Spotify.db"
connection = sqlite3.connect(file_name)

connection.execute('CREATE TABLE IF NOT EXISTS ' +
    '"toptracks" ("name" TEXT,' +
    '"rank" INT, ' +
    '"id" INT, ' +
    '"trackID" TEXT, ' +
    '"artists" TEXT, ' +
    '"trackNUM" INT, ' +
    '"duration" INT, ' +
    '"popularity" INT, ' +
    '"previewURL" TEXT, ' +
    '"session_key" TEXT, ' +
    '"term_length" TEXT)'
)

connection.execute('CREATE TABLE IF NOT EXISTS ' +
    'topartists (name TEXT,' +
    'rank INT, ' +
    'id TEXT, ' +
    'popularity INT, ' +
    'session_key TEXT, ' +
    'term_length TEXT)'
)
