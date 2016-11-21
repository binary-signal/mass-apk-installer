"""
 Name:        encryption_support
 Author:      Evaggelos Mouroutsos

 Created:     19/10/2011
 Last Modified: 22/11/2016
 Copyright:   (c) Evaggelos Mouroutsos 2016
 Licence:
 Copyright (c) 2016, Evaggelos Mouroutsos
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
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.   """""

import os
import sys
import hashlib
import random
import struct
import stat
from Crypto import Random
from Crypto.Cipher import AES

class encryption_support(object):


    # define exit states
    BAD_FILE = -3
    NORMAL_EXIT = 0
    block_size =16
    # make sure block data size for AES is correct in the current implementation
    if AES.block_size != 16:
        block_size = 16  # the default should be 16 bytes (128 bits)
    else:  # if not then
        block_size = AES.block_size  # the AES standard operates on 128 bit data blocks
    def __init__(self, key_aes):
        if key_aes==None: # if key_aes is empty generate random key 16 byte / 128 bit in length for the AES cipher key
            self.key_aes = Random.get_random_bytes(16)
            self.dump_aes_key(self.key_aes)
        if key_aes != None:
            self.key_aes =self.hash_sha256(key_aes)
            if len(self.hash_sha256(key_aes)) != self.block_size:
                print "Aes key size missmatch !"
                return None

    # the function generates encrypted files with the extension
    # *.enc encrypted files are stored in the specified format
    # below {[file size in bytes][IV][Cipher blocks]}.enc
    def encrypt_aes(self, input_file, encrypted_file):
        # sanity check for input file to be encrypted
        if self.file_permission(input_file) == False:
            print("Can't read input file check file permissions")
            return None
        # get the input file size in bytes
        filesize = os.path.getsize(input_file)
        print('File path: ' + os.path.abspath(input_file))
        print('Size: ' + str(filesize))

        # initialise IV a.k.a initialization vector for the AES encryption
        # with random data 16 byte long each byte has a value from 0-255
        # (0xff) in hexx aka unsigned integer values
        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))

        # make an AES object with key,mode and iv
        aes_obj = AES.new(self.key_aes, AES.MODE_CBC, iv)

        with open(input_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:

                # encode file size of input file to be encrypted as unsigned long long
                # in little-endian byte order before we store it to encrypted file
                outfile.write(struct.pack('<Q', filesize))  # place the encoded file size
                # at the start of the enctypted file followed by the IV vector, IV vector
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
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)

                    # encrypt babe!
                    cipher_text = aes_obj.encrypt(chunk)

                    # append cipher to output file
                    outfile.write(cipher_text)
        return encrypted_file


    # decrypt encrypted file to plain text files blah blah....
    def decrypt_aes(self, encrypted_file, decrypted_file):
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:

                # read the first 8 bytes which is the file size stored in the ecrypted file
                origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]

                # read the IV stored in the encrypted file
                iv = infile.read(16)

                # make an aes object for the decryption
                aes_obj = AES.new(self.key_aes, AES.MODE_CBC, iv)

                while True:
                    # read block sizes of 128 bit from cipher text
                    chunk = infile.read(self.block_size)
                    if len(chunk) == 0:  # reached EOF
                        break

                    # decrypt cipher as if there is no tomorrow
                    plain_text = aes_obj.decrypt(chunk)

                    # write the plain data to a file
                    outfile.write(plain_text)

                    # delete padding bytes from decoded file
                    outfile.truncate(origsize)
        return decrypted_file


    # make file check sum using SHA-256 hash function
    def make_hash_sha256(self, in_filename, block_size=1024):
        # sanity check on file permissions
        if not self.file_permission(in_filename):
            sys.exit(self.BAD_FILE)

        # open file
        file = open(in_filename, 'r')

        # make sha256 object
        sha256 = hashlib.sha256()

        # read chunks of the file
        while True:
            data = file.read(block_size)
            if not data:
                break

            # update the new hash
            sha256.update(data)

        # close file return hash in hexx
        file.close()
        return sha256.hexdigest()



    # make file check sum using SHA-256 hash function
    def hash_sha256(self, data):
        # make sha256 object
        sha256 = hashlib.sha256()
        # update the new hash
        sha256.update(data)
        return sha256.hexdigest()


    # sanity checks input file for size permissions etc...
    # we consider we have write permissions for the output files
    # generated in cwd
    def file_permission(self, file_path):
        # file sanity check
        c1 = os.path.isfile(file_path)

        # size sanity check
        c2 = os.path.getsize(file_path)

        # read access sanity check
        st = os.stat(file_path)
        c3 = bool(st.st_mode & stat.S_IRGRP)
        return (c1 and c2 and c3)


    def dump_SHA256(self, str_hash, hash_file):
        # save computed hash value to file: hash_file

        with open(hash_file, 'wb') as outfile:
            outfile.write(str_hash)


    # START DEBUG CODE TO BE REMOVED

    # bad practise to store encryption keys in plain text but it's for debugging
    def dump_aes_key(self, key, key_file='aes.key'):
        # output file is hardcoded, the key file will be overwritten
        # in the next program execution with a new key generated randomly

        with open(key_file, 'wb') as outfile:
            outfile.write(key)


    # compare the sha256 hash from the original and the decoded to
    # find out if they math in case we did a job with encryption or decryption
    def integrity_hash_check(self, f_original, f_decoded):
        h1 = self.make_hash_sha256(f_original)
        h2 = self.make_hash_sha256(f_decoded)
        print('h1: ' + h1)
        print('h2: ' + h2)
        if (h1 == h2):
            print('Hash\'s match\n')
        elif (h1 != h2):
            print('Hash\'s don\'t matchBAD\n')



