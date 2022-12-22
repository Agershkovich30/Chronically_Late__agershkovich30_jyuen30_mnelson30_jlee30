'''
Creates database of top tracks
'''
def create(cursor, list, start, key, term_length):
    ID_counter = 0
    query = "INSERT OR IGNORE INTO toptracks( 'name', 'rank', 'id', 'trackID', 'artists', 'trackNUM', 'duration', 'popularity', 'previewURL', 'session_key', 'term_length'"
    query += f") VALUES"
    for item in list:
        if str(list[ID_counter].get("name")).find('"') != -1:
            query += "('" + str(list[ID_counter].get("name")) + "', "
        else:
            query += '("' + str(list[ID_counter].get("name")) + '", '
        query += f'{ID_counter + start}, "'
        query += str(list[ID_counter].get("id")) + '", '
        query += '"' + str(list[ID_counter].get("id")) + '", '
        if str(list[ID_counter].get("artists")[0]).find('"') != -1:
            query += "('" + str(list[ID_counter].get("artists")[0]) + "', "
        else:
            query += '"' + str(list[ID_counter].get("artists")[0].get("name")) + '", '
        query += str(list[ID_counter].get("track_number")) + ', '
        query += str(list[ID_counter].get("duration_ms")) + ', '
        query += str(list[ID_counter].get("popularity")) + ', '
        query += '"' + str(list[ID_counter].get("preview_url")) + '", '
        query += '"' + key + '", '
        query += '"' + term_length
        query += '"), \n'
        ID_counter += 1
    query = query[:-3]
    cursor.execute(query)
    cursor.connection.commit()
    return query

'''
Gets all values in the database that have the specified value.
'''
def get(cursor, **kwargs):
    query = "SELECT * FROM toptracks WHERE "
    for key, value in kwargs.items():
        query += f'"{key}" = "{value}" AND '
    query = query[:-5]
    cursor.execute(query)
    blog = cursor.fetchone()
    return blog
