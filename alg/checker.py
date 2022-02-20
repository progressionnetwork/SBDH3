import imagehash
import numpy as np
from PIL import Image
import sqlite3
import os
import ppdeep
from py_essentials import hashing as hs


def compare_hashes(fname_db, hash_imagehash, hash_str):
    cutoff = 5  # maximum bits that could be different between the hashes.
    hash1 = hash_imagehash
    hash2 = imagehash.hex_to_hash(hash_str.encode())
    #print(hash1)
    #print(hash2)
    #print("cutoff",hash1 - hash2)
    if hash1 == hash2:
        print(fname_db, 'images are similar')
        return True

    if hash1 - hash2 < cutoff:
        print(fname_db, 'images are similar, similarity', hash1 - hash2)
        return True
    else:
        #print(fname_db,'images are not similar')
        return False


if __name__ == '__main__':

    savedir = "preview"
    img = '408.png'
    IS_SIMILAR = False

    img_name = os.path.basename(img)
    img_size = str(os.path.getsize(img_name))
    sha1_hash = hs.fileChecksum(img_name, "sha1")
    ssdeep_hash = ppdeep.hash_from_file(img_name)
    img_handle = Image.open(img_name)
    average_hash = imagehash.average_hash(img_handle, hash_size=8)
    phash = imagehash.phash(img_handle, hash_size=8)
    dhash = imagehash.dhash(img_handle, hash_size=8)
    img_handle.close()

    conn = sqlite3.connect("indexed.db")
    # conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    rows = cursor.execute("SELECT fname, size, sha1, ssdeep, averagehash, phash, dhash FROM images").fetchall()
    #print(rows)

    for row in rows:
        fname_db, size_db, sha1_hash_db, ssdeep_hash_db, average_hash_db, phash_db, dhash_db = list(row)
        #print(fname_db, size_db, sha1_hash_db, ssdeep_hash_db)

        if sha1_hash == sha1_hash_db:
            print(fname_db, 'SHA1 Hashes are same! Same file!')
            IS_SIMILAR = True

        if img_size == int(size_db):
            print(fname_db, 'Size of siles are same! Same file?')

        similarity = ppdeep.compare(ssdeep_hash, ssdeep_hash_db)
        if similarity > 80:
            print(similarity)
            print(fname_db, 'Images are very similar')
            IS_SIMILAR = True

        if compare_hashes(fname_db, average_hash, average_hash_db):
            IS_SIMILAR = True
        if compare_hashes(fname_db, phash, phash_db):
            IS_SIMILAR = True
        if compare_hashes(fname_db, dhash, dhash_db):
            IS_SIMILAR = True

        if IS_SIMILAR:
            print('Verdict: Similar')

        IS_SIMILAR = False

    print('DONE.')