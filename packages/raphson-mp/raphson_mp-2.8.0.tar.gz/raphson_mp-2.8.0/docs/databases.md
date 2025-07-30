# Databases

The application stores data using several SQLite databases in `/data`. Files in this directory must never be deleted. If you want to start fresh, you can delete ALL databases.

## `music.db`

This is the main database. All important data is stored here, like accounts, settings, playback history, and an index of music files and metadata. It should not get larger than a few megabytes.

## `cache.db`

The cache database is used to store the result of expensive operations. For example, it stores transcoded audio, lyrics, album cover images and thumbnails. The database size varies depending on your usage, but expect it to be around 10GB for every 1000 tracks.

This database, like other databases, must not be deleted. If you have accidentally deleted it, also delete the `cache` directory if it exists, and then create the database using the SQL commands in `raphson_mp/sql/cache.sql`.

## `meta.db`

This database stores information about the database version, allowing the app to run the correct database migrations during an upgrade.

## `offline.db`

The offline database stores downloaded track data when the music player operates in [offline mode](./offline.md). It is **not** safe to delete this database. See the [offline mode wiki page](./offline.md) for instructions on how to safely delete downloaded tracks.

## `errors.log`

This is a text file containing all log messages with a `WARNING` level or higher. After acknowledging the warnings, you may empty the file using `truncate -s 0 errors.log`.

## Performing manual vacuum, converting database to INCREMENTAL_VACUUM

1. Open old database
2. Run `PRAGMA auto_vacuum = INCREMENTAL`
3. Run `VACUUM INTO 'new.db'`
4. Close database
5. Open new database
6. Run `PRAGMA journal_mode = WAL`
7. Close database
8. Shut down music player and move new database in place
