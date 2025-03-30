import heapq
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pickle  # For tree serialization
import threading

# Huffman Node class
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def __repr__(self):
        return f"HuffmanNode(char={self.char}, freq={self.freq})"

# Build Huffman Tree
def build_huffman_tree(frequency):
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

# Generate Huffman Codes
def generate_huffman_codes(root, current_code="", codes={}):
    if root is None:
        return

    if root.char is not None:
        codes[root.char] = current_code

    generate_huffman_codes(root.left, current_code + "0", codes)
    generate_huffman_codes(root.right, current_code + "1", codes)

    return codes

# Encode text
def encode_text(text, codes):
    return ''.join([codes[char] for char in text])

# Decode text
def decode_text(encoded_text, root):
    decoded_text = ""
    current = root

    for bit in encoded_text:
        current = current.left if bit == '0' else current.right
        if current.char:
            decoded_text += current.char
            current = root

    return decoded_text

# Serialize the Huffman Tree
def serialize_tree(root):
    return pickle.dumps(root)  # Using pickle to serialize the tree

# Deserialize the Huffman Tree
def deserialize_tree(serialized_tree):
    return pickle.loads(serialized_tree)

# File Compression Function with Progress Bar
def compress_file(progress_bar):
    file_paths = filedialog.askopenfilenames()
    if not file_paths:
        return

    total_files = len(file_paths)
    for index, file_path in enumerate(file_paths):
        with open(file_path, 'r') as file:
            text = file.read()

        frequency = {char: text.count(char) for char in set(text)}
        root = build_huffman_tree(frequency)
        codes = generate_huffman_codes(root)
        encoded_text = encode_text(text, codes)

        # Serialize the tree to prepend to the compressed file
        serialized_tree = serialize_tree(root)

        compressed_file = file_path + ".bin"
        with open(compressed_file, "wb") as file:
            # Write the serialized tree first (length of tree + the tree itself)
            file.write(len(serialized_tree).to_bytes(4, 'big'))  # Storing the length of the tree
            file.write(serialized_tree)
            file.write(encoded_text.encode())  # Then write the encoded text

        # Update progress bar
        progress_bar['value'] = ((index + 1) / total_files) * 100
        progress_bar.update()
    
    messagebox.showinfo("Success", f"Files compressed successfully!")

# File Decompression Function
def decompress_file(progress_bar):
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    with open(file_path, "rb") as file:
        # Read the length of the serialized tree and then the serialized tree
        tree_length = int.from_bytes(file.read(4), 'big')
        serialized_tree = file.read(tree_length)
        encoded_text = file.read().decode()

    # Deserialize the tree
    root = deserialize_tree(serialized_tree)

    # Decode the text using the deserialized tree
    decoded_text = decode_text(encoded_text, root)
    decompressed_file = file_path.replace(".bin", "_decompressed.txt")

    with open(decompressed_file, "w") as file:
        file.write(decoded_text)

    messagebox.showinfo("Success", f"File decompressed and saved as {decompressed_file}")

# GUI Application with Progress Bar
def create_gui():
    root = tk.Tk()
    root.title("Huffman Compression Tool")
    root.geometry("500x250")

    # Adding GUI elements
    tk.Label(root, text="Huffman File Compression", font=("Arial", 14)).pack(pady=10)
    
    # Progress Bar
    progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
    progress_bar.pack(pady=10)

    def compress_with_progress():
        threading.Thread(target=compress_file, args=(progress_bar,)).start()

    def decompress_with_progress():
        threading.Thread(target=decompress_file, args=(progress_bar,)).start()

    tk.Button(root, text="Compress Files", command=compress_with_progress).pack(pady=5)
    tk.Button(root, text="Decompress File", command=decompress_with_progress).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

# Run GUI
create_gui()
