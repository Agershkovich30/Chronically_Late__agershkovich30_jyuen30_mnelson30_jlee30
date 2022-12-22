'''
Creates database of Top Artists
'''
def create(cursor, list, start, key, term_length):
    ID_counter = 0
    query = "INSERT OR IGNORE INTO topartists('name', 'rank', 'id', 'popularity', 'session_key', 'term_length'"
    query += f") VALUES"
    for item in list:
        if str(list[ID_counter].get("name")).find('"') != -1:
            query += "('" + str(list[ID_counter].get("name")) + "', "
        else:
            query += '("' + str(list[ID_counter].get("name")) + '", '
        query += f'{ID_counter + start}, "'
        query += str(list[ID_counter].get("id")) + '", '
        query += str(list[ID_counter].get("popularity")) + ", "
        query += "'" + key + "', "
        query += "'" + term_length
        query += "'), \n"
        ID_counter += 1
    query = query[:-3]
    cursor.execute(query)
    cursor.connection.commit()
    return query

'''
Gets all values in the database that have the specified value.
'''
def get(cursor, **kwargs):
    query = "SELECT * FROM topartists WHERE "
    for key, value in kwargs.items():
        query += f"{key} = '{value}' AND "
    query = query[:-5]
    cursor.execute(query)
    blog = cursor.fetchone()
    return blog

def update(cursor, id, **kwargs):
    query = "UPDATE topartists SET "
    for key, value in kwargs.items():
        query += f"{key} = '{value}', "
    query = query[:-2]
    query += f" WHERE id = '{id}'"
    cursor.execute(query)
    cursor.connection.commit()
    return None