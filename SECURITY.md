# Security Policy

## Lapor masalah di repo ini

Menemukan kredensial asli, secret, atau lubang di repo ini sendiri? Hubungi owner repo langsung, rotate kredensialnya dulu, jangan buka public issue dengan detailnya.

## Secret scanning

`gitleaks dir .` dari root repo harus bersih sebelum push.
Token contoh di dokumentasi skill terdaftar di `.gitleaksignore` berdasarkan fingerprint. Tidak ada kredensial asli yang diabaikan, dan secret baru tetap ketahuan.
