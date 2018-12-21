import pickledb

for port in [3000, 3001, 3002, 3003]:
    print("Values for port: {}".format(port))
    pickle_filename = "assignment3_" + str(port) + ".db"
    db = pickledb.load(pickle_filename, False)
    for key in db.getall():
        print("{}: {}".format(key, db.get(key)))