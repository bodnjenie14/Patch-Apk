# All credit to tehfens https://github.com/d-fens/tstoapkpatcher/
# - Glitched Panda

'''
MIT License

Copyright (c) 2025 d-fens

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
  
import os
import sys
import struct
import binascii
import hashlib
import r2pipe

new_url = os.environ['DLC_URL']
buffer_size = hex(len(new_url) + 1)
string_size = hex(len(new_url))
print("URL buffer size: %s, URL string size: %s" % (buffer_size, string_size))

# for patching use ghidra and check the functions used for accessing the DLC URL
# patching is required for the string allocations to ensure that the correct buffer size is copied
patching_rules = {
  '8137faf7a4349043e6e0b0516249c673eb402cf96012c87d805c969cdccae3c2': {
    'name': 'lib/arm64-v8a/libscorpio.so',
    'checks': [
      "px 90 @ 0x00373230",
      "pd 1 @ 0x012cd644",
      "pd 1 @ 0x012cd674",
      "pd 1 @ 0x012cd6b4",
    ],
    'patches': [
      "w %s @ 0x00373230" % str(new_url),
      "wa mov w0,%s @ 0x012cd644" % (buffer_size),
      "wa add x9,x0,%s @ 0x012cd674" % (buffer_size),
      "wa add x9,x0,%s @ 0x012cd6b4" % (string_size),
    ]
  },
  '5b6bf2e4ee386a825e58c3e12aae923d66db8b6fbdd21df05b81b4e1edeb44ae': {
    'name': 'lib/arm64-v8a/libscorpio-neon.so',
    'checks': [
      "px 90 @ 0x00373227",
      "pd 1 @ 0x012cc6fc",
      "pd 1 @ 0x012cc72c",
      "pd 1 @ 0x012cc76c",
    ],
    'patches': [
      "w %s @ 0x00373227" % str(new_url),
      "wa mov w0,%s @ 0x012cc6fc" % (buffer_size),
      "wa add x9,x0,%s @ 0x012cc72c" % (buffer_size),
      "wa add x0,x0,%s @ 0x012cc76c" % (string_size),
    ]
  },
  '9eae61f7ae7ae3a8880809e7ffab33e5ae63582d6ad2d941d539d65639a6a47a': {
    'name': 'lib/armeabi-v7a/libscorpio.so',
    'checks': [
      "px 90 @ 0x00300c08",
      "pd 1 @ 0x011c1398",
      "pd 1 @ 0x011c13c8",
      "pd 1 @ 0x011c13e4",
      "pd 1 @ 0x011c13f4",
    ],
    'patches': [
      "w %s @ 0x00300c08" % str(new_url),
      "wa mov r0,%s @ 0x011c1398" % (buffer_size),
      "wa add r0,r5,%s @ 0x011c13c8" % (buffer_size),
      "wa mov r2,%s @ 0x011c13e4" % (string_size),
      "wa add r0,r5,%s @ 0x011c13f4" % (string_size),
    ]
  },
  '7f4d355773c8a7328c9ee405f11b8795ca95fd2dbf7755fa686ea900593cbee3': {
    'name': 'lib/armeabi-v7a/libscorpio-neon.so',
    'checks': [
      "px 90 @ 0x002f0c08",
      "pd 1 @ 0x011bdaac",
      "pd 1 @ 0x011bdadc",
      "pd 1 @ 0x011bdaf8",
      "pd 1 @ 0x011bdb08",
    ],
    'patches': [
      "w %s @ 0x002f0c08" % str(new_url),
      "wa mov r0,%s @ 0x011bdaac" % (buffer_size),
      "wa add r0,r5,%s @ 0x011bdadc" % (buffer_size),
      "wa mov r2,%s @ 0x011bdaf8" % (string_size),
      "wa add r0,r5,%s @ 0x011bdb08" % (string_size),
    ]
  }
}

decompiled_path = os.environ['SOURCE_OUTPUT']
attempt_files_to_patch = [
  os.path.join(decompiled_path, "lib/armeabi-v7a/libscorpio-neon.so"), os.path.join(decompiled_path, "lib/armeabi-v7a/libscorpio.so"),
  os.path.join(decompiled_path, "lib/arm64-v8a/libscorpio-neon.so"), os.path.join(decompiled_path, "lib/arm64-v8a/libscorpio.so"),
]

def patch_check(f, patch_rule):
  r = r2pipe.open(f, flags=["-w"])
  # show values before patching
  for cmd in patch_rule["checks"]:
    print(r.cmd(cmd))

  # patch the binary
  for cmd in patch_rule["patches"]:
    r.cmd(cmd)

  # check the values after patching
  for cmd in patch_rule["checks"]:
    print(r.cmd(cmd))

for f in attempt_files_to_patch:
  with open(f, 'rb') as fd:
    hash = hashlib.file_digest(fd, "sha256")
    if hash.hexdigest() in patching_rules:
      patch_rule = patching_rules[hash.hexdigest()]
      print("Attempt: ", patch_rule["name"], f)
      patch_check(f, patch_rule)
    else:
      print("BAD: couldn't find checks to perform against ", f)
