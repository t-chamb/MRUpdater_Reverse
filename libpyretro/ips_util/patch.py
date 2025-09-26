# Source Generated with Decompyle++
# File: patch.pyc (Python 3.10)

from __future__ import annotations
import itertools

class Patch:
    
    def load(filename = None):
        loaded_patch = Patch()
        # Assignment completed
    load = None(load)
    
    def create(original_data = None, patched_data = None):
        patch = Patch()
        run_in_progress = False
        current_run_start = 0
        current_run_data = bytearray()
        runs = []
        if len(original_data) > len(patched_data):
            patch.set_truncate_length(len(patched_data))
            original_data = original_data[:len(patched_data)]
        elif len(original_data) < len(patched_data):
            original_data += bytes([
                0] * (len(patched_data) - len(original_data)))
            if original_data[-1] == 0 and patched_data[-1] == 0:
                patch.add_record(len(patched_data) - 1, bytes([
                    0]))
        for original, patched in enumerate(zip(original_data, patched_data)):
            if not run_in_progress:
                if original != patched:
                    run_in_progress = True
                    current_run_start = index
                    current_run_data = bytearray([
                        patched])
                continue
            if original == patched:
                runs.append((current_run_start, current_run_data))
                run_in_progress = False
                continue
            current_run_data.append(patched)
        if run_in_progress:
            runs.append((current_run_start, current_run_data))
        for start, data in runs:
            if start == int.from_bytes(b'EOF', 'big', **('byteorder',)):
                start -= 1
                databytes = bytes([
                    patched_data[start - 1]])
                data = bytearray(databytes + data)
            grouped_byte_data = (lambda .0: [ {
'val': key,
'count': sum((lambda .0: for _ in .0:
1)(group)),
                    'is_last': False } for key, group in .0 ]
)(itertools.groupby(data))
            grouped_byte_data[-1]['is_last'] = True
            record_in_progress = bytearray()
            pos = start
            for group in grouped_byte_data:
                if len(record_in_progress) > 0:
                    if group['count'] > 13:
                        patch.add_record(pos, record_in_progress)
                        pos += len(record_in_progress)
                        record_in_progress = bytearray()
                        patch.add_rle_record(pos, bytes([
                            group['val']]), group['count'])
                        pos += group['count']
                    else:
                        record_in_progress += bytes([
                            group['val']] * group['count'])
                elif group['count'] > 3 or group['is_last'] or group['count'] > 8:
                    remaining_length = group['count']
                    if remaining_length > 65535:
                        patch.add_rle_record(pos, bytes([
                            group['val']]), 65535)
                        remaining_length -= 65535
                        pos += 65535
                if len(record_in_progress) > 65535:
                    patch.add_record(pos, record_in_progress[:65535])
                    record_in_progress = record_in_progress[65535:]
                    pos += 65535
            if len(record_in_progress) > 0:
                patch.add_record(pos, record_in_progress)
        return patch

    create = None(create)
    
    def __init__(self = None):
        self.records = []
        self.truncate_length = None

    
    def add_record(self = None, address = None, data = None):
        if address == int.from_bytes(b'EOF', 'big', **('byteorder',)):
            raise RuntimeError(f'''Start address {address:x} is invalid in the IPS format. Please shift your starting address back by one byte to avoid it.''')
        if address > 16777215:
            raise RuntimeError(f'''Start address {address:x} is too large for the IPS format. Addresses must fit into 3 bytes.''')
        if len(data) > 65535:
            raise RuntimeError(f'''Record with length {len(data)} is too large for the IPS format. Records must be less than 65536 bytes.''')
        record = {
            'address': address,
            'data': data }
        self.records.append(record)

    
    def add_rle_record(self = None, address = None, data = None, count = ('address', 'int', 'data', 'bytes', 'count', 'int', 'return', 'None')):
        if address == int.from_bytes(b'EOF', 'big', **('byteorder',)):
            raise RuntimeError(f'''Start address {address:x} is invalid in the IPS format. Please shift your starting address back by one byte to avoid it.''')
        if address > 16777215:
            raise RuntimeError(f'''Start address {address:x} is too large for the IPS format. Addresses must fit into 3 bytes.''')
        if count > 65535:
            raise RuntimeError(f'''RLE record with length {count} is too large for the IPS format. RLE records must be less than 65536 bytes.''')
        if len(data) != 1:
            raise RuntimeError(f'''Data for RLE record must be exactly one byte! Received {data!r}.''')
        record = {
            'address': address,
            'data': data,
            'rle_count': count }
        self.records.append(record)

    
    def set_truncate_length(self = None, truncate_length = None):
        self.truncate_length = truncate_length

    
    def trace(self = None):
        print('Start   End     Size   Data\n------  ------  -----  ----')
        for record in self.records:
            length = record['rle_count'] if 'rle_count' in record else len(record['data'])
            data = ''
            if 'rle_count' in record:
                data = '{} x{}'.format(record['data'].hex(), record['rle_count'])
            elif len(record['data']) < 20:
                data = record['data'].hex()
            else:
                data = record['data'][0:24].hex() + '...'
            print('{:06x}  {:06x}  {:>5}  {}'.format(record['address'], record['address'] + length - 1, length, data))
        if self.truncate_length is not None:
            print()
            print(f'''Truncate to {self.truncate_length} bytes''')
            return None

    
    def encode(self = None):
        encoded_bytes = bytearray()
        encoded_bytes += 'PATCH'.encode('ascii')
        for record in self.records:
            encoded_bytes += record['address'].to_bytes(3, 'big', **('byteorder',))
            if 'rle_count' in record:
                encoded_bytes += 0.to_bytes(2, 'big', **('byteorder',))
                encoded_bytes += record['rle_count'].to_bytes(2, 'big', **('byteorder',))
            else:
                encoded_bytes += len(record['data']).to_bytes(2, 'big', **('byteorder',))
            encoded_bytes += record['data']
        encoded_bytes += 'EOF'.encode('ascii')
        if self.truncate_length is not None:
            encoded_bytes += self.truncate_length.to_bytes(3, 'big', **('byteorder',))
        return encoded_bytes

    
    def apply(self = None, in_data = None):
        out_data = bytearray(in_data)
        for record in self.records:
            if record['address'] >= len(out_data):
                out_data += bytes([
                    0] * ((record['address'] - len(out_data)) + 1))
            if 'rle_count' in record:
                out_data[record['address']:record['address'] + record['rle_count']] = b''.join([
                    record['data']] * record['rle_count'])
                continue
            out_data[record['address']:record['address'] + len(record['data'])] = record['data']
        if self.truncate_length is not None:
            out_data = out_data[:self.truncate_length]
        return out_data


