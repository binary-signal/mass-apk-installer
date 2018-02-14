#!/usr/bin/env python

"""
 Name:        encryption
 Author:      Evan 

 Created:     19/10/2011
 Last Modified: 12/02/2018
 Copyright:   (c) Evan 2018
 Licence:
 Copyright (c) 2018, Evan
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
     * Neither the name of the <organization> nor the
       names of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 vWARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 """

import os
import hashlib
import struct
import stat

from Crypto.Cipher import AES
import progressbar as pb


# sanity checks input file for size permissions etc...
# we consider we have write permissions for the output files
# generated in cwd
def is_ok_file_permission(file_path):
    # file sanity check
    c1 = os.path.isfile(file_path)

    # size sanity check
    c2 = os.path.getsize(file_path)

    # read access sanity check
    st = os.stat(file_path)
    c3 = bool(st.st_mode & stat.S_IRGRP)
    return not (c1 and c2 and c3)

    # make file check sum using SHA-256 hash function


def sha256_file(in_filename, block_size=1024):
    # open file
    try:
        file = open(in_filename, 'rb')
    except FileNotFoundError:
        raise ValueError("file {} doesn't exists".format(in_filename))

    # make sha256 object
    sha256 = hashlib.sha256()

    # read chunks of the file
    while True:
        data = file.read(block_size)
        if not data:
            break

        # update the new hash
        sha256.update(data)

    # close file return hash in hex
    file.close()
    return sha256.hexdigest()

    # make file check sum using SHA-256 hash function


def hash_sha256(data):
    # make sha256 object
    sha256 = hashlib.sha256()
    # update the new hash
    sha256.update(data.encode('utf-8'))

    return sha256.hexdigest()


def validate_sha256(f_original, f_decoded):
    # compare the sha256 hash from the original and the decoded to
    # find out if they math in case we did a job with encryption or decryption
    h1 = sha256_file(f_original)
    h2 = sha256_file(f_decoded)
    print('{}: {}'.format(f_original, h1))
    print('{}: {}'.format(f_decoded, h2))
    if h1 == h2:
        print('Hash\'s match\n')
    elif h1 != h2:
        raise ValueError("Hashes don't match")


def integrity_check(hash_str, file):
    # check a hash against a file
    if hash_str == sha256_file(file):
        print('Hash\'s match\n')
    else:
        raise ValueError("Hashes don't match")


class AesEncryption(object):
    def __init__(self, key_aes):
        self.block_size = 16
        self.key_aes = hash_sha256(key_aes)[:self.block_size]

    # the function generates encrypted files with the extension
    # *.enc encrypted files are stored in the specified format
    # below {[file size in bytes][IV][Cipher blocks]}.enc
    def encrypt(self, input_file, encrypted_file):
        # sanity check for input file to be encrypted
        if is_ok_file_permission(input_file):
            raise ValueError("Can't read input file check file permissions")

        # get the input file size in bytes
        size = os.path.getsize(input_file)

        iteration = size / self.block_size

        # initialize widgets
        widgets = ['progress: ', pb.Percentage(), ' ',
                   pb.Bar(), ' ', pb.ETA()]
        # initialize timer
        timer = pb.ProgressBar(widgets=widgets, maxval=iteration+1).start()
        count = 0

        # initialise IV a.k.a initialization vector for the AES encryption
        # with random data 16 byte long each byte has a value from 0-255
        # (0xff) in hex aka unsigned integer values
        iv = os.urandom(self.block_size)

        # make an AES object with key,mode and iv
        aes_obj = AES.new(self.key_aes, AES.MODE_CBC, iv)

        with open(input_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:

                # encode file size of input file to be encrypted as unsigned long long
                # in little-endian byte order before we store it to encrypted file
                outfile.write(struct.pack('<Q', size))  # place the encoded file size
                # at the start of the encrypted file followed by the IV vector, IV vector
                # isn't a secret nor a key so we can store it/publish it in order to do
                # decryption later
                outfile.write(iv)

                while True:
                    # read 128 bit of data to encrypt
                    chunk = infile.read(self.block_size)
                    if len(chunk) == 0:  # we reached EOF
                        break

                    # check if data length is 128 bit if not
                    # do zero padding
                    elif len(chunk) % self.block_size != 0:
                        chunk += ' '.encode('utf-8') * (self.block_size - len(chunk) % self.block_size)

                    # encrypt babe!
                    cipher_text = aes_obj.encrypt(chunk)

                    # append cipher to output file
                    outfile.write(cipher_text)

                    # update progress bar
                    count += 1
                    timer.update(count)
                timer.finish()
        return encrypted_file

    # decrypt encrypted file to plain text files blah blah....
    def decrypt(self, encrypted_file, decrypted_file):
        if is_ok_file_permission(encrypted_file):
            raise ValueError("Can't read input file check file permissions")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:

                # read the first 8 bytes which is the file size stored in the encrypted file
                origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]

                # read the IV stored in the encrypted file
                iv = infile.read(self.block_size)

                # make an aes object for the decryption
                aes_obj = AES.new(self.key_aes, AES.MODE_CBC, iv)

                # get the input file size in bytes
                size = os.path.getsize(encrypted_file)
                iteration = size / self.block_size

                # initialize widgets
                widgets = ['progress: ', pb.Percentage(), ' ',
                           pb.Bar(), ' ', pb.ETA()]
                # initialize timer
                timer = pb.ProgressBar(widgets=widgets, maxval=iteration).start()
                count = 0

                try:
                    while True:
                        # read block sizes of 128 bit from cipher text
                        chunk = infile.read(self.block_size)
                        if len(chunk) == 0:  # reached EOF
                            break

                        # decrypt cipher as if there is no tomorrow
                        plain_text = aes_obj.decrypt(chunk)

                        # write the plain data to a file
                        outfile.write(plain_text)

                        # update progress bar
                        count += 1
                        timer.update(count)

                    # delete padding bytes from decoded file
                    outfile.truncate(origsize)
                    # finish
                    timer.finish()
                except Exception:
                    print("FUCK")
                    pass
        return decrypted_file
