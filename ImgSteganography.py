import streamlit as st
import cv2
import numpy as np
from PIL import Image

def encrypt_image(img, message):
    # STORE MESSAGE LENGTH IN FIRST PIXEL
    length = len(message)
    img[0, 0, 0] = (length >> 16) & 0xFF
    img[0, 0, 1] = (length >> 8) & 0xFF
    img[0, 0, 2] = length & 0xFF

    # STORE MESSAGE IN SUBSEQUENT PIXELS
    n, m, z = 1, 1, 0
    for c in message:
        img[n, m, z] = ord(c)
        n += 1
        m += 1
        z = (z + 1) % 3
    return img

def decrypt_image(img):
    # EXTRACT MESSAGE LENGTH FROM FIRST PIXEL
    byte1 = img[0, 0, 0]
    byte2 = img[0, 0, 1]
    byte3 = img[0, 0, 2]
    length = (byte1 << 16) | (byte2 << 8) | byte3

    # EXTRACT MESSAGE FROM SUBSEQUENT PIXELS
    message = []
    n, m, z = 1, 1, 0
    for _ in range(length):
        message.append(chr(img[n, m, z]))
        n += 1
        m += 1
        z = (z + 1) % 3
    return ''.join(message)

st.title("Image Steganography App")
tab_encrypt, tab_decrypt = st.tabs(["Encrypt", "Decrypt"])

with tab_encrypt:
    st.header("Encrypt a Message")
    st.write("Please upload an image file to encrypt the message.")
    upload_encrypt = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="encrypt")
    message = st.text_input("Secret Message")
    
    if upload_encrypt and message:
        if st.button("Encrypt Message"):
            try:
                # READ AND PROCESS IMAGE
                file_bytes = np.asarray(bytearray(upload_encrypt.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                encrypted_img = encrypt_image(img.copy(), message)
                
                # DISPLAY AND DOWNLOAD IMAGE
                st.image(Image.fromarray(cv2.cvtColor(encrypted_img, cv2.COLOR_BGR2RGB)), 
                        caption="Encrypted Image")
                _, encoded_image = cv2.imencode(".png", encrypted_img)
                st.download_button(
                    label="Download Encrypted Image",
                    data=encoded_image.tobytes(),
                    file_name="encrypted.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab_decrypt:
    st.header("Decrypt a Message")
    st.write("Upload the encrypted image to decrypt the message.")
    upload_decrypt = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="decrypt")
    
    if upload_decrypt and st.button("Decrypt Message"):
        try:
            # READ AND PROCESS IMAGE
            file_bytes = np.asarray(bytearray(upload_decrypt.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            decrypted_msg = decrypt_image(img)
            
            # DISPLAY DECRYPTED MESSAGE
            st.success("Decrypted Message:")
            st.code(decrypted_msg)
        except Exception as e:
            st.error(f"Error: {str(e)}")