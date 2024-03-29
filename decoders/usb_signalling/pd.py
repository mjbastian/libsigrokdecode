##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2011 Gareth McMullin <gareth@blacksphere.co.nz>
## Copyright (C) 2012-2013 Uwe Hermann <uwe@hermann-uwe.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
##

import sigrokdecode as srd

'''
OUTPUT_PYTHON format:

Packet:
[<ptype>, <pdata>]

<ptype>, <pdata>:
 - 'SOP', None
 - 'SYM', <sym>
 - 'BIT', <bit>
 - 'STUFF BIT', None
 - 'EOP', None

<sym>:
 - 'J', 'K', 'SE0', or 'SE1'

<bit>:
 - 0 or 1
 - Note: Symbols like SE0, SE1, and the J that's part of EOP don't yield 'BIT'.
'''

# Low-/full-speed symbols.
# Note: Low-speed J and K are inverted compared to the full-speed J and K!
symbols = {
    'low-speed': {
        # (<dp>, <dm>): <symbol/state>
        (0, 0): 'SE0',
        (1, 0): 'K',
        (0, 1): 'J',
        (1, 1): 'SE1',
    },
    'full-speed': {
        # (<dp>, <dm>): <symbol/state>
        (0, 0): 'SE0',
        (1, 0): 'J',
        (0, 1): 'K',
        (1, 1): 'SE1',
    },
}

bitrates = {
    'low-speed': 1500000,   # 1.5Mb/s (+/- 1.5%)
    'full-speed': 12000000, # 12Mb/s (+/- 0.25%)
}

class Decoder(srd.Decoder):
    api_version = 1
    id = 'usb_signalling'
    name = 'USB signalling'
    longname = 'Universal Serial Bus (LS/FS) signalling'
    desc = 'USB (low-speed and full-speed) signalling protocol.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['usb_signalling']
    probes = [
        {'id': 'dp', 'name': 'D+', 'desc': 'USB D+ signal'},
        {'id': 'dm', 'name': 'D-', 'desc': 'USB D- signal'},
    ]
    optional_probes = []
    options = {
        'signalling': ['Signalling', 'full-speed'],
    }
    annotations = [
        ['sym', 'Symbol'],
        ['sop', 'Start of packet (SOP)'],
        ['eop', 'End of packet (EOP)'],
        ['bit', 'Bit'],
        ['stuffbit', 'Stuff bit'],
    ]
    annotation_rows = (
        ('bits', 'Bits', (1, 2, 3, 4)),
        ('symbols', 'Symbols', (0,)),
    )

    def __init__(self):
        self.samplerate = None
        self.oldsym = 'J' # The "idle" state is J.
        self.ss_sop = None
        self.ss_block = None
        self.samplenum = 0
        self.syms = []
        self.bitrate = None
        self.bitwidth = None
        self.bitnum = 0
        self.samplenum_target = None
        self.oldpins = None
        self.consecutive_ones = 0
        self.state = 'IDLE'

    def start(self):
        self.out_python = self.register(srd.OUTPUT_PYTHON)
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value
            self.bitrate = bitrates[self.options['signalling']]
            self.bitwidth = float(self.samplerate) / float(self.bitrate)
            self.halfbit = int(self.bitwidth / 2)

    def putpx(self, data):
        self.put(self.samplenum, self.samplenum, self.out_python, data)

    def putx(self, data):
        self.put(self.samplenum, self.samplenum, self.out_ann, data)

    def putpm(self, data):
        s, h = self.samplenum, self.halfbit
        self.put(self.ss_block - h, s + h, self.out_python, data)

    def putm(self, data):
        s, h = self.samplenum, self.halfbit
        self.put(self.ss_block - h, s + h, self.out_ann, data)

    def putpb(self, data):
        s, h = self.samplenum, self.halfbit
        self.put(s - h, s + h, self.out_python, data)

    def putb(self, data):
        s, h = self.samplenum, self.halfbit
        self.put(s - h, s + h, self.out_ann, data)

    def set_new_target_samplenum(self):
        bitpos = self.ss_sop + (self.bitwidth / 2)
        bitpos += self.bitnum * self.bitwidth
        self.samplenum_target = int(bitpos)

    def wait_for_sop(self, sym):
        # Wait for a Start of Packet (SOP), i.e. a J->K symbol change.
        if sym != 'K':
            self.oldsym = sym
            return
        self.ss_sop = self.samplenum
        self.set_new_target_samplenum()
        self.putpx(['SOP', None])
        self.putx([1, ['SOP']])
        self.state = 'GET BIT'

    def handle_bit(self, sym, b):
        if self.consecutive_ones == 6 and b == '0':
            # Stuff bit.
            self.putpb(['STUFF BIT', None])
            self.putb([4, ['SB: %s' % b]])
            self.putb([0, ['%s' % sym]])
            self.consecutive_ones = 0
        else:
            # Normal bit (not a stuff bit).
            self.putpb(['BIT', b])
            self.putb([3, ['%s' % b]])
            self.putb([0, ['%s' % sym]])
            if b == '1':
                self.consecutive_ones += 1
            else:
                self.consecutive_ones = 0

    def get_eop(self, sym):
        # EOP: SE0 for >= 1 bittime (usually 2 bittimes), then J.
        self.syms.append(sym)
        self.putpb(['SYM', sym])
        self.putb([0, ['%s' % sym]])
        self.bitnum += 1
        self.set_new_target_samplenum()
        self.oldsym = sym
        if self.syms[-2:] == ['SE0', 'J']:
            # Got an EOP.
            self.putpm(['EOP', None])
            self.putm([2, ['EOP']])
            self.bitnum, self.syms, self.state = 0, [], 'IDLE'
            self.consecutive_ones = 0

    def get_bit(self, sym):
        if sym == 'SE0':
            # Start of an EOP. Change state, run get_eop() for this bit.
            self.state = 'GET EOP'
            self.ss_block = self.samplenum
            self.get_eop(sym)
            return
        self.syms.append(sym)
        self.putpb(['SYM', sym])
        b = '0' if self.oldsym != sym else '1'
        self.handle_bit(sym, b)
        self.bitnum += 1
        self.set_new_target_samplenum()
        self.oldsym = sym

    def decode(self, ss, es, data):
        if self.samplerate is None:
            raise Exception("Cannot decode without samplerate.")
        for (self.samplenum, pins) in data:
            # State machine.
            if self.state == 'IDLE':
                # Ignore identical samples early on (for performance reasons).
                if self.oldpins == pins:
                    continue
                self.oldpins = pins
                sym = symbols[self.options['signalling']][tuple(pins)]
                self.wait_for_sop(sym)
            elif self.state in ('GET BIT', 'GET EOP'):
                # Wait until we're in the middle of the desired bit.
                if self.samplenum < self.samplenum_target:
                    continue
                sym = symbols[self.options['signalling']][tuple(pins)]
                if self.state == 'GET BIT':
                    self.get_bit(sym)
                elif self.state == 'GET EOP':
                    self.get_eop(sym)
            else:
                raise Exception('Invalid state: %s' % self.state)

