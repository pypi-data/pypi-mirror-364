import csv
from .types import FPETypeHandler

class FPECSVHandler:
    def __init__(self, key: bytes, tweak: bytes, mode: str = "FF3-1"):
        self.handler = FPETypeHandler(key, tweak, mode)

    def encrypt_csv(self, input_path: str, output_path: str, formats: list):
        with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            headers = next(reader)
            writer.writerow(headers)
            for row in reader:
                encrypted_row = []
                for value, fmt in zip(row, formats):
                    if fmt == 'DATE':
                        encrypted_row.append(self.handler.encrypt_date(value))
                    elif fmt == 'FLOAT':
                        encrypted_row.append(self.handler.encrypt_float(value))
                    elif fmt == 'STRING':
                        encrypted_row.append(self.handler.encrypt_string(value))
                    elif fmt == 'DIGITS':
                        val = value if len(value) % 2 == 0 else '0' + value
                        enc_val = self.handler.fpe.encrypt(val)
                        encrypted_row.append(enc_val[-len(value):] if len(value) % 2 != 0 else enc_val)
                    else:
                        encrypted_row.append(value)
                writer.writerow(encrypted_row)

    def decrypt_csv(self, input_path: str, output_path: str, formats: list):
        with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            headers = next(reader)
            writer.writerow(headers)
            for row in reader:
                decrypted_row = []
                for value, fmt in zip(row, formats):
                    if fmt == 'DATE':
                        decrypted_row.append(self.handler.decrypt_date(value))
                    elif fmt == 'FLOAT':
                        decrypted_row.append(self.handler.decrypt_float(value))
                    elif fmt == 'STRING':
                        decrypted_row.append(self.handler.decrypt_string(value))
                    elif fmt == 'DIGITS':
                        val = value if len(value) % 2 == 0 else '0' + value
                        dec_val = self.handler.fpe.decrypt(val)
                        decrypted_row.append(dec_val[-len(value):] if len(value) % 2 != 0 else dec_val)
                    else:
                        decrypted_row.append(value)
                writer.writerow(decrypted_row)