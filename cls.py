def remove_duplicate_lines(input_file='admin.txt', output_file='result.txt'):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        
        # Menghapus duplikat dan menjaga urutan
        unique_lines = list(dict.fromkeys(line.strip() for line in lines))
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(unique_lines))
        
        print(f"Duplikat berhasil dihapus! Hasilnya disimpan di {output_file}.")
    except FileNotFoundError:
        print(f"File {input_file} tidak ditemukan. Pastikan file input ada di direktori yang sama.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    remove_duplicate_lines()
