# Ejemplos rápidos para probar la API

1) Obtener token (JWT):

curl -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d '{"username":"admin","password":"adminpass"}'

Respuesta: {"access": "<token>", "refresh": "<token>"}

2) Usar token para listar furgones:

curl -H "Authorization: Bearer <access>" http://127.0.0.1:8000/api/furgones/

3) Actualizar ubicación de un furgón (id=1):

curl -X POST http://127.0.0.1:8000/api/furgones/1/update_location/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"latitude": -33.45, "longitude": -70.66, "reported_at": "2025-11-20T08:30:00"}'

4) Crear notificación:

curl -X POST http://127.0.0.1:8000/api/notificaciones/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"tipo":"evento","mensaje":"El furgón llegará con 5 minutos de retraso","furgon":1}'

5) Marcar notificación como leída (id=1):

curl -X POST http://127.0.0.1:8000/api/notificaciones/1/marcar_leida/ \
  -H "Authorization: Bearer <access>"

  HTTPie examples (más legible que curl):

  1) Obtener token:

  http POST http://127.0.0.1:8000/api/token/ username=admin password=adminpass

  2) Listar furgones (con token):

  http GET http://127.0.0.1:8000/api/furgones/ "Authorization:Bearer <access>"

  3) Actualizar ubicación (update_location):

  http POST http://127.0.0.1:8000/api/furgones/1/update_location/ latitude=-33.45 longitude=-70.66 reported_at="2025-11-20T08:30:00" "Authorization:Bearer <access>"

  PowerShell (Invoke-RestMethod) examples:

  # Obtener token
  $body = @{ username = 'admin'; password = 'adminpass' } | ConvertTo-Json
  $token = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/token/' -Method Post -Body $body -ContentType 'application/json'

  # Usar token para listar furgones
  Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/furgones/' -Headers @{ Authorization = "Bearer $($token.access)" }

  # Actualizar ubicación
  $payload = @{ latitude = -33.45; longitude = -70.66 } | ConvertTo-Json
  Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/furgones/1/update_location/' -Method Post -Body $payload -ContentType 'application/json' -Headers @{ Authorization = "Bearer $($token.access)" }
