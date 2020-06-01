#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
os.system('fab --user sentry --password sentry destroy_all')
os.system('fab --user sentry --password sentry setup')

