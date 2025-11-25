import sys
import re
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except Exception:
    print('PyPDF2 no está instalado en este entorno. Instálese antes de ejecutar el script.')
    sys.exit(2)


def extract_text(path):
    reader = PdfReader(path)
    text = []
    for p in reader.pages:
        try:
            t = p.extract_text()
        except Exception:
            t = ''
        if t:
            text.append(t)
    return "\n".join(text)


def find_snippets(text, keywords, context_chars=100):
    snippets = {}
    for k in keywords:
        snippets[k] = []
    for k in keywords:
        for m in re.finditer(re.escape(k), text, flags=re.IGNORECASE):
            start = max(0, m.start()-context_chars)
            end = min(len(text), m.end()+context_chars)
            snippets[k].append(text[start:end].replace('\n', ' '))
    return snippets


def find_attributes(text):
    # búsqueda simple de patrones tipo "- atributo: tipo" o "atributo: tipo"
    pattern = re.compile(r"([A-Za-z0-9_áéíóúñÁÉÍÓÚÑ ]{2,60})[:\-]\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    return pattern.findall(text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python extract_pdf.py <ruta_pdf>')
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f'Archivo no encontrado: {pdf_path}')
        sys.exit(1)

    print('Leyendo:', pdf_path)
    text = extract_text(str(pdf_path))

    if not text.strip():
        print('No se extrajo texto del PDF (posible PDF escaneado).')
        sys.exit(0)

    print('\n--- Inicio del texto extraído (primeros 3000 caracteres) ---\n')
    print(text[:3000])
    print('\n--- Fin del extracto ---\n')

    keywords = [
        'Conductor', 'Estudiante', 'Furgon', 'Furgón', 'Ruta', 'Colegio', 'Apoderado',
        'Registrar', 'patente', 'licencia', 'capacidad', 'telefono', 'direccion', 'rut',
        'asignar', 'reporte', 'horario',
    ]

    snippets = find_snippets(text, keywords, context_chars=250)
    print('\nResumen por palabras clave (snippet):')
    for k, s in snippets.items():
        if s:
            print(f"\n[{k}] {len(s)} ocurrencia(s). Primer snippet:\n")
            print(s[0][:800])

    attrs = find_attributes(text)
    if attrs:
        print('\nAtributos detectados (posibles pares nombre/tipo):')
        for a, t in attrs[:80]:
            print('-', a.strip(), ':', t.strip())
    else:
        print('\nNo se detectaron atributos con el patrón simple.')

    # extraer posibles encabezados (líneas cortas en mayúscula inicial)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates = []
    for ln in lines:
        if 2 < len(ln) < 120 and ln[0].isupper():
            candidates.append(ln)
    print('\nPosibles encabezados o títulos (primeros 40):')
    for c in candidates[:40]:
        print('-', c)

    print('\nExtracción completa.')
