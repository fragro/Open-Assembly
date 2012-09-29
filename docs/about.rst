What is Open Assembly?
=======================================================

Open Assembly is an open source internet decision making framework. Main features include

- Create ideas and upload content and vote on the content
- Browse ideas based on collective approval, controversy, and more
- Users can create groups to host their ideas with variable settings for decision making and user inclusion
- Trust Network that will provide Open Assembly with the tools to deter Sock Puppets
- Coming Soon: Gamification concepts such as currency and classes. 

The goal is to develop a fully functional Augmented Reality Game where users act out actions in the real world and are rewarded in the virtual world, a global forum where ideas can be peer-reviewed and tested, allowing users to achieve critical mass on the best ideas to change the world.

Technology
------------

OA is built on Django-nonrel and MongoDB. We use Redis to provide caching and pub/sub. A node.js server allows OA to host dynamic chat and notification messages. We also have provided a Solr search server configured with OA to allow efficient and powerful search capabilities.

OA doesn't follow the traditional Django views style. For more info check out :ref:`templatetags`


History
------------

Open Assembly


License
------------

Copyright (c) 2012, Frank Grove
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Open Assembly nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL FRANK GROVE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.