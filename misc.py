# -*- coding: utf-8 -*-

import uuid


class Misc:

    @staticmethod
    def uuid():
        return str(uuid.uuid4())
