import imagehash
from PIL import Image
import ppdeep
from py_essentials import hashing as hs
from django.core.files.base import File as DjangoFile

from comparator.models import ImageCheck


def load_image(image):
    im = ImageCheck.objects.create()
    im.img.save(image.name, DjangoFile(image))

    img_name = im.img.path
    sha1_hash = hs.fileChecksum(img_name, "sha1")
    ssdeep_hash = ppdeep.hash_from_file(img_name)
    img_handle = Image.open(img_name)
    average_hash = imagehash.average_hash(img_handle, hash_size=8)
    phash = imagehash.phash(img_handle, hash_size=8)
    dhash = imagehash.dhash(img_handle, hash_size=8)
    img_handle.close()

    im.sha1 = sha1_hash
    im.ssdeep = ssdeep_hash
    im.averagehash = average_hash
    im.phash = phash
    im.dhash = dhash

    im.save()

    images = ImageCheck.objects.all()
    res = []
    for img2 in images:
        is_similar = compare(sha1_hash, img2.sha1,
                      ssdeep_hash, img2.ssdeep,
                      average_hash, img2.averagehash,
                      phash, img2.phash,
                      dhash, img2.dhash)
        if is_similar:
            res.append('http://137.184.112.242:5000' + img2.img.url)

    return {
        "ssdeep": ssdeep_hash,
        "sha1": sha1_hash,
        "similar": res
    }


def compare_hashes(hash_imagehash, hash_str):
    cutoff = 5  # maximum bits that could be different between the hashes.
    hash1 = hash_imagehash
    hash2 = imagehash.hex_to_hash(hash_str.encode())

    if hash1 == hash2:
        return True

    if hash1 - hash2 < cutoff:
        return True
    else:
        return False


def compare(sha1_hash,sha1_hash_db,
            ssdeep_hash,ssdeep_hash_db,
            average_hash,average_hash_db,
            phash,phash_db,
            dhash,dhash_db):
    IS_SIMILAR = False

    if sha1_hash == sha1_hash_db:
        IS_SIMILAR = True

    similarity = ppdeep.compare(ssdeep_hash, ssdeep_hash_db)
    if similarity > 80:
        IS_SIMILAR = True

    if compare_hashes(average_hash, average_hash_db):
        IS_SIMILAR = True
    if compare_hashes(phash, phash_db):
        IS_SIMILAR = True
    if compare_hashes(dhash, dhash_db):
        IS_SIMILAR = True

    return IS_SIMILAR

