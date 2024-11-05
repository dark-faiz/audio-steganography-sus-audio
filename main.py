from flask import Flask, request, jsonify, send_file
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import base64
import io

app = Flask(__name__)

# ... (existing encrypt_data and hide_data_in_audio functions)

@app.route('/hide', methods=['POST'])
def hide_data():
    audio_file = request.files['audio_file']
    secret_file = request.files['secret_file']
    key = request.form['key']
    date = request.form['date']

    try:
        # Encrypt the secret file data
        iv, encrypted_data = encrypt_data(secret_file, key)

        # Hide the encrypted data in the audio file
        stego_audio_path = 'uploads/stego_audio.wav'  # Save path for the stego audio
        hide_data_in_audio(audio_file, encrypted_data)

        return jsonify(success=True, message='Data hidden successfully', path=stego_audio_path)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

@app.route('/extract', methods=['POST'])
def extract_data():
    audio_file = request.files['audio_file']
    key = request.form['key']

    try:
        # Extract the hidden data from the audio file
        extracted_data = extract_hidden_data(audio_file)
        
        # Decrypt the extracted data
        iv, encrypted_data = extracted_data
        decrypted_data = decrypt_data(encrypted_data, key)

        return jsonify(success=True, message='Data extracted successfully', data=decrypted_data)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

def extract_hidden_data(audio_file):
    audio = open(audio_file, 'rb')
    audio_bytes = bytearray(audio.read())
    
    # Read the bits from the audio bytes
    extracted_bits = ''
    for byte in audio_bytes:
        extracted_bits += str(byte & 1)  # Get the least significant bit

    # Convert bits back to bytes
    byte_array = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte_array.append(int(extracted_bits[i:i + 8], 2))

    # The first 16 bytes is the IV
    iv = byte_array[:16]
    encrypted_data = byte_array[16:]  # The rest is the encrypted data
    
    return base64.b64encode(iv).decode('utf-8'), base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_data(encrypted_data, key):
    key = key.ljust(32)[:32].encode('utf-8')  # Adjust the key length
    cipher = AES.new(key, AES.MODE_CBC, iv=base64.b64decode(encrypted_data[0]))  # Use the extracted IV
    decrypted_data = unpad(cipher.decrypt(base64.b64decode(encrypted_data[1])), AES.block_size)
    return decrypted_data

if __name__ == "__main__":
    app.run(debug=True)
