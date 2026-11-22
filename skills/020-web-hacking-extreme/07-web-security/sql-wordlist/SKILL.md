# SQL Wordlist

Wordlist injeksi SQL dan fuzzing web, dari **orwagodfather/SQL-Wordlist**.

Sumber: https://github.com/orwagodfather/SQL-Wordlist

## File

- `sql.txt` — 1.080 payload injeksi SQL (UNION SELECT, time-based, error-based, auth bypass).
- `everything-00.txt` s.d. `everything-09.txt` — 1.308.121 baris wordlist fuzzing umum (path, file, parameter). Dipecah per 1,8 MB supaya bisa masuk repo. 697 baris dibersihkan mengikuti aturan repo ini.

## Satukan lagi

```bash
cat everything-*.txt > everything.txt
```

## Cara pakai

```bash
# Fuzzing parameter dengan ffuf
ffuf -w sql.txt -u 'https://target/search?q=FUZZ'

# Wordlist umum buat directory fuzzing
ffuf -w everything.txt -u 'https://target/FUZZ'

# sqlmap dengan wordlist sendiri
sqlmap -u 'https://target/item?id=1' --wordlist sql.txt
```

## Catatan

- `everything.txt` aslinya satu file 16,6 MB; versi repo ini dipecah 10 bagian, isi sama persis setelah disatukan.
- Baris-barisnya payload mentah — cocokkan encoding target sebelum dipakai (ada yang URL-encoded, ada yang mentah).
