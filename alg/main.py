import time
import urllib
import hashlib
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
from os import walk
import json
from PIL import Image
import imagehash
import sqlite3
from py_essentials import hashing as hs
import ppdeep
import pathlib
import sys
from os import listdir
from os.path import isfile, join
from typing import Dict, List, Tuple
import imagehash
import numpy as np
from PIL import Image

savedir = "preview"

def calculate_signature(image_file: str, hash_size: int) -> np.ndarray:
    """
    Calculate the dhash signature of a given file

    Args:
        image_file: the image (path as string) to calculate the signature for
        hash_size: hash size to use, signatures will be of length hash_size^2

    Returns:
        Image signature as Numpy n-dimensional array or None if the file is not a PIL recognized image
    """
    pil_image = Image.open(image_file).convert("L").resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS)
    dhash = imagehash.dhash(pil_image, hash_size)
    signature = dhash.hash.flatten()
    pil_image.close()
    return signature


def find_near_duplicates(input_dir: str, threshold: float, hash_size: int, bands: int) -> List[Tuple[str, str, float]]:
    """
    Find near-duplicate images

    Args:
        input_dir: Directory with images to check
        threshold: Images with a similarity ratio >= threshold will be considered near-duplicates
        hash_size: Hash size to use, signatures will be of length hash_size^2
        bands: The number of bands to use in the locality sensitve hashing process

    Returns:
        A list of near-duplicates found. Near duplicates are encoded as a triple: (filename_A, filename_B, similarity)
    """
    rows: int = int(hash_size ** 2 / bands)
    signatures = dict()
    hash_buckets_list: List[Dict[str, List[str]]] = [dict() for _ in range(bands)]

    # Build a list of candidate files in given input_dir
    file_list = [join(input_dir, f) for f in listdir(input_dir) if isfile(join(input_dir, f))]

    # Iterate through all files in input directory
    for fh in file_list:
        try:
            signature = calculate_signature(fh, hash_size)
        except IOError:
            # Not a PIL image, skip this file
            continue

        # Keep track of each image's signature
        signatures[fh] = np.packbits(signature)

        # Locality Sensitive Hashing
        for i in range(bands):
            signature_band = signature[i * rows:(i + 1) * rows]
            signature_band_bytes = signature_band.tobytes()
            if signature_band_bytes not in hash_buckets_list[i]:
                hash_buckets_list[i][signature_band_bytes] = list()
            hash_buckets_list[i][signature_band_bytes].append(fh)

    # Build candidate pairs based on bucket membership
    candidate_pairs = set()
    for hash_buckets in hash_buckets_list:
        for hash_bucket in hash_buckets.values():
            if len(hash_bucket) > 1:
                hash_bucket = sorted(hash_bucket)
                for i in range(len(hash_bucket)):
                    for j in range(i + 1, len(hash_bucket)):
                        candidate_pairs.add(
                            tuple([hash_bucket[i], hash_bucket[j]])
                        )

    # Check candidate pairs for similarity
    near_duplicates = list()
    for cpa, cpb in candidate_pairs:
        hd = sum(np.bitwise_xor(
            np.unpackbits(signatures[cpa]),
            np.unpackbits(signatures[cpb])
        ))
        similarity = (hash_size ** 2 - hd) / hash_size ** 2
        if similarity > threshold:
            near_duplicates.append((cpa, cpb, similarity))

    # Sort near-duplicates by descending similarity and return
    near_duplicates.sort(key=lambda x: x[2], reverse=True)
    return near_duplicates


# SSDEEP hashing
def fuzzyhash_images(images_list):
    all_hashes = []
    for img in images_list:
        file = savedir + '/' + img
        hash = ppdeep.hash_from_file(file)
        all_hashes.append(hash)
        print(f'File: {file}, ssdeep: {hash}')


# Average hashing
def averagehash_images(images_list):
    all_hashes = []
    for img in images_list:
        file = savedir + '/' + img
        hash = imagehash.average_hash(Image.open(file), hash_size=16)
        all_hashes.append(hash)
        print(f'File: {file}, ssdeep: {hash}')


# Perceptual hashing
def phash_images(images_list):
    all_hashes = []
    for img in images_list:
        file = savedir + '/' + img
        hash = imagehash.phash(Image.open(file), hash_size=12)
        all_hashes.append(hash)
        print(f'File: {file}, ssdeep: {hash}')


# Difference  hashing
def dhash_images(images_list):
    all_hashes = []
    for img in images_list:
        file = savedir + '/' + img
        hash = imagehash.dhash(Image.open(file), hash_size=12)
        all_hashes.append(hash)
        print(f'File: {file}, ssdeep: {hash}')


# SHA1 hashing
def sha1hash_images(images_list):
    all_hashes = []
    for img in images_list:
        file = savedir + '/' + img
        hash = hs.fileChecksum(file, "sha1")
        all_hashes.append(hash)
        print(f'File: {file}, sha1: {hash}')


def compare_images():
    hash_orig = '98304:nP10dW4Zul+87vA2trigm0tzd3WFb1qpLjS1mAr9hO3f+B7:nPSbElBvtlltPWIe1mlPK'  # ppdeep.hash_from_file("img/906.png")
    hash_smashed = '98304:FYcHemuUwHY0pThivs2hfQ/omcjoRVgPcSRaRcPdplMA/QYizsqAVEKj9h+Xb3r1:FrHe5hHY0p4k2C3TgPjplPMzoVEO9wD5'  # ppdeep.hash_from_file("img/906 - Copy.png")

    print(hash_orig)
    print(hash_smashed)
    similarity = ppdeep.compare(hash_orig, hash_smashed)

    print(similarity)


def list_images():
    filenames = [item for item in os.listdir(savedir) if os.path.isfile(os.path.join(savedir, item))]
    return filenames


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

    data = []
    attributes_selected = ['fname', 'size', 'sha1', 'ssdeep']
    images_list = list_images()

    i = 0
    for img in images_list:
        item = {"id": str(i)}
        for attribute in attributes_selected:
            if attribute.img == img:
                item[attribute.attribute.name] = attribute.value
        data.append(item)
        i += 1

    json_dump = json.dumps(data)

    print(json_dump)

    exit(0)

    ACTION = 'check'
    savedir = "preview"

    if ACTION == 'index':
        conn = sqlite3.connect("indexed.db")  # или :memory: чтобы сохранить в RAM
        cursor = conn.cursor()

        # Создание таблицы
        cursor.execute("""CREATE TABLE images
                          (fname text, size text, sha1 text,
                           ssdeep text, averagehash text, phash text, dhash text)
                       """)

        images_list = list_images()

        for img in images_list:
            img_name = savedir+'/'+os.path.basename(img)
            print(img_name)
            img_size = str(os.path.getsize(img_name))
            sha1_hash = hs.fileChecksum(img_name, "sha1")
            ssdeep_hash = ppdeep.hash_from_file(img_name)
            img_handle = Image.open(img_name)
            average_hash = imagehash.average_hash(img_handle, hash_size=8)
            phash = imagehash.phash(img_handle, hash_size=8)
            dhash = imagehash.dhash(img_handle, hash_size=8)
            img_handle.close()

            cursor.execute(f"""INSERT INTO images
                              VALUES ('{img_name}', '{img_size}', '{sha1_hash}',
                              '{ssdeep_hash}', '{average_hash}', '{phash}', '{dhash}')"""
                           )
        conn.commit()

    if ACTION == 'check':

        img = 'smashed.png'
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

    exit(0)
    input_dir = "img/"
    threshold = 0.9
    hash_size = 16
    bands = 16

    try:
        near_duplicates = find_near_duplicates(input_dir, threshold, hash_size, bands)
        if near_duplicates:
            print(f"Found {len(near_duplicates)} near-duplicate images in {input_dir} (threshold {threshold:.2%})")
            for a, b, s in near_duplicates:
                print(f"{s:.2%} similarity: file 1: {a} - file 2: {b}")
        else:
            print(f"No near-duplicates found in {input_dir} (threshold {threshold:.2%})")
    except OSError:
        print(f"Couldn't open input directory {input_dir}")

    #
    # hashes = sha1hash_images(images_list)
    #main()
