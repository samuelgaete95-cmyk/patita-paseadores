import flet as ft
import requests

SUPABASE_URL = "https://oerhxswjwpestxcmncft.supabase.co"
SUPABASE_KEY = "sb_publishable_p75QcrIUZn_vU30Jf6W1VA_wiknlpHD"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

def obtener_paseadores():
    url = f"{SUPABASE_URL}/rest/v1/paseadores?select=*"
    try:
        resp = requests.get(url, headers=HEADERS)
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def ica_catalogo_view(page: ft.Page):
    paseadores = obtener_paseadores()
    
    lista_tarjetas = ft.ListView(expand=1, spacing=10, padding=10, width=380)
    
    for p in paseadores:
        lista_tarjetas.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(p.get("nombre", "Sin nombre"), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(f"📍 Zona: {p.get('zona', 'N/A')}", size=13, color=ft.Colors.GREY_400),
                    ft.Text(f"💰 Tarifa: ${p.get('tarifa', 0)}", size=13, color="#00E676"),
                    ft.Text(f"📞 Contacto: {p.get('instagram', 'N/A')}", size=13, color="#4392F1"),
                ], spacing=4),
                bgcolor="#181B20", padding=15, border_radius=12,
                border=ft.border.all(1, "#2B303A")
            )
        )

    if not paseadores:
        lista_tarjetas.controls.append(ft.Text("No hay paseadores registrados aún.", color=ft.Colors.GREY_400))

    def volver_atras(e):
        page.route = "/"
        page.update()

    btn_volver = ft.ElevatedButton(
        text="⬅️ Volver al Registro",
        on_click=volver_atras,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#4392F1", shape=ft.RoundedRectangleBorder(radius=12)),
        width=340
    )

    return ft.View(
        route="/catalogo",
        controls=[
            ft.Container(height=10),
            ft.Text("🐾 PASEADORES DISPONIBLES", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=5),
            lista_tarjetas,
            ft.Container(height=10),
            btn_volver
        ],
        bgcolor="#121417",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20
    )