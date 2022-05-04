def write_id(id):
    file = open('../chat_server/id.txt','w')
    id = id+1
    file.write(str(id))
    file.close()


def get_write_id():
    file = open('../chat_server/id.txt','r')
    index = int(file.read())
    write_id(index)
    file.close()
    return index

def set_1():
    file = open('../chat_server/id.txt','w')
    file.write('1')
    file.close()
    return 1

def get_just_id():
    file = open('../chat_server/id.txt','r')
    index = int(file.read())
    file.close()
    return index
