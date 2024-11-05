from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import wave

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'supersecretkey'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper function to handle file saving
def save_file(file, subfolder):
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, filename)
    file.save(file_path)
    return file_path

# Load an audio file for LSB manipulation
def load_audio(file_path):
    return wave.open(file_path, 'rb')

# Function to hide data in audio file using LSB steganography
def hide_data(audio, data):
    data_bin = ''.join(format(byte, '08b') for byte in data)
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Modify LSBs to hide the data
    for i in range(len(data_bin)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(data_bin[i])

    # Save the modified audio
    modified_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'stego_audio.wav')
    modified_audio = wave.open(modified_audio_path, 'wb')
    modified_audio.setparams(audio.getparams())
    modified_audio.writeframes(bytes(frame_bytes))
    audio.close()
    modified_audio.close()

    return modified_audio_path

# Function to encrypt a file using AES-256
def encrypt_file(file_path, key):
    iv = get_random_bytes(16)  # 16 bytes for AES-256 CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(file_path, 'rb') as f:
        data = f.read()

    # Padding to make data a multiple of 16
    padding_length = 16 - len(data) % 16
    data += bytes([padding_length]) * padding_length

    ciphertext = cipher.encrypt(data)
    encrypted_file_path = f"{file_path}.enc"

    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + ciphertext)

    return encrypted_file_path

# Route to render the main form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle hiding data in an audio file
@app.route('/hide', methods=['POST'])
def hide():
    audio_file = request.files['audio_file']
    secret_file = request.files['secret_file']

    # Save files
    audio_path = save_file(audio_file, 'audio')
    secret_path = save_file(secret_file, 'secret')

    # Read secret data
    with open(secret_path, 'rb') as f:
        secret_data = f.read()

    # Load audio and hide data
    audio = load_audio(audio_path)
    stego_audio_path = hide_data(audio, secret_data)

    return jsonify(success=True, message="Data hidden successfully.", path=stego_audio_path)

# Route to handle encryption of the stego audio file
@app.route('/encrypt', methods=['POST'])
def encrypt():
    stego_audio_path = request.form['stego_audio_path']
    key = request.form['key'].encode('utf-8')
    
    # Ensure the key length is 32 bytes for AES-256
    if len(key) != 32:
        return jsonify(success=False, message="Key must be 32 bytes (256 bits) long.")

    # Encrypt the stego audio
    encrypted_file_path = encrypt_file(stego_audio_path, key)

    return jsonify(success=True, message="File encrypted successfully.", path=encrypted_file_path)

# Route to handle decryption (Optional)
@app.route('/decrypt', methods=['POST'])
def decrypt():
    encrypted_file = request.files['encrypted_file']
    key = request.form['key'].encode('utf-8')
    
    if len(key) != 32:
        return jsonify(success=False, message="Key must be 32 bytes (256 bits) long.")

    encrypted_file_path = save_file(encrypted_file, 'encrypted')

    with open(encrypted_file_path, 'rb') as f:
        iv = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(ciphertext)

    # Remove padding
    padding_length = decrypted_data[-1]
    decrypted_data = decrypted_data[:-padding_length]

    decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted_audio.wav')
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

    return jsonify(success=True, message="File decrypted successfully.", path=decrypted_file_path)

if __name__ == '__main__':
    app.run(debug=True)


