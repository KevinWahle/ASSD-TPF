import base64
import os
import PyPDF2
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def concat_name(input_file, str):
    i = 0
    temp_name = ''
    while input_file[i] != '.':
        temp_name = temp_name + input_file[i]
        i += 1
    return temp_name + str


def generate_key(input_file, password):
    try:
        # Derive a 256-bit key from the password using PBKDF2 with a random salt
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        # Save the key to a file
        with open(concat_name(input_file, ".key"), 'wb') as key_file:
            key_file.write(key)
        return key
    except Exception as e:
        print(f"Error generating key: {e}")


def encrypt_pdf(input_file):
    try:
        # Generate a key from the password
        key = generate_key(input_file, "password")

        # Open the input PDF file and create a PDF writer object
        with open(input_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()

            # Encode the key to a string of up to 32 characters and use it as the owner password
            owner_pwd = base64.urlsafe_b64encode(key)[:32].decode()

            # Encrypt the output PDF with the key and the user password
            pdf_writer.encrypt(user_password=owner_pwd, owner_pwd=owner_pwd, use_128bit=True)

            # Add each page of the input PDF to the output PDF
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # Write the output PDF to a new file
            with open(concat_name(input_file, "_encrypted.pdf"), 'wb') as output:
                pdf_writer.write(output)

        print("PDF file encrypted successfully!")
    except Exception as e:
        print(f"Error encrypting PDF: {e}")
        os.remove(concat_name(input_file, ".key"))



def decrypt_pdf(input_file):
    try:
        # Read the key from the key file
        with open(concat_name(input_file, ".key"), 'rb') as key_file:
            key = key_file.read()

        # Open the input PDF file and create a PDF file reader object
        with open(concat_name(input_file, "_encrypted.pdf"), 'rb') as file:
            # Create a PDF file reader object with the decryption parameters
            pdf_reader = PyPDF2.PdfReader(file)
            if pdf_reader.is_encrypted:
                pdf_reader.decrypt(base64.urlsafe_b64encode(key)[:32].decode())

            # Create a PDF writer object and add each page of the input PDF to it
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # Write the output PDF to a new file
            with open(input_file, 'wb') as output:
                pdf_writer.write(output)

        os.remove(concat_name(input_file, ".key"))
        print("PDF file decrypted successfully!")
    except Exception as e:
        print(f"Error decrypting PDF: {e}")



# Example usage
#encrypt_pdf('input.pdf')
#decrypt_pdf('input.pdf')
