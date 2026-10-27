import flet as ft
import requests
import random
import threading
from supabase import create_client, Client

SUPABASE_URL = "https://oerhxswjwpestxcmncft.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9lcmh4c3dqd3Blc3R4Y21uY2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI4Njc5MTAsImV4cCI6MjEwODQ0MzkxMH0.IitByKppWvs2Ky7N0J98gU1ZjrfedZcD4rYdlYPJ8jM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "PATITA - Red de Paseadores"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121417"
    page.padding = 15
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.window.width = 420
    page.window.height = 780

    paseador_logueado = {"id": None, "nombre": "", "zona": "", "tarifa": ""}

    # CAMPOS REGISTRO / LOGIN
    txt_nombre = ft.TextField(label="Nombre Completo", hint_text="Ej: Samuel Gaete", border_color="#4392F1", color=ft.Colors.WHITE, prefix_icon=ft.Icons.PERSON)
    txt_zona = ft.TextField(label="Zona de Paseo", hint_text="Ej: Curicó Centro", border_color="#4392F1", color=ft.Colors.WHITE, prefix_icon=ft.Icons.LOCATION_ON)
    txt_tarifa = ft.TextField(label="Tarifa por hora ($)", hint_text="Ej: 3000", keyboard_type=ft.KeyboardType.NUMBER, border_color="#4392F1", color=ft.Colors.WHITE, prefix_icon=ft.Icons.ATTACH_MONEY)
    txt_clave_reg = ft.TextField(label="Crear Clave (Letras y Números)", hint_text="Ej: patita2026", password=True, can_reveal_password=True, border_color="#4392F1", color=ft.Colors.WHITE, prefix_icon=ft.Icons.LOCK)
    lbl_resultado_reg = ft.Text(value="", size=12, weight=ft.FontWeight.BOLD)

    txt_login_nombre = ft.TextField(label="Tu Nombre Registrado", border_color="#4392F1", color=ft.Colors.WHITE, prefix_icon=ft.Icons.PERSON)
    txt_login_clave = ft.TextField(label="Clave de Acceso", password=True, can_reveal_password=True, border_color="#4392F1", color=ft.Colors.WHITE, prefix_icon=ft.Icons.LOCK)
    lbl_resultado_login = ft.Text(value="", size=12, weight=ft.FontWeight.BOLD)

    lista_catalogo = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
    contenido_dinamico = ft.Container(expand=True)

    # COMPONENTES DE CHAT
    chat_mensajes = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    txt_mensaje_input = ft.TextField(hint_text="Escribe tu mensaje...", border_color="#4392F1", color=ft.Colors.WHITE, expand=True)
    lbl_chat_destino = ft.Text("Chat", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    
    chat_target = {"paseador_id": None, "remitente_tipo": "Cliente"}

    def actualizar_contador_mensajes():
        if not paseador_logueado["id"]:
            return
        try:
            res = supabase.table("mensajes").select("*").eq("paseador_id", paseador_logueado["id"]).execute()
            total = len(res.data) if res.data else 0
            if total > 0:
                btn_menu_chat.text = f"Mi Chat ({total})"
                btn_menu_chat.style = ft.ButtonStyle(bgcolor="#4392F1", color=ft.Colors.WHITE, padding=6)
            else:
                btn_menu_chat.text = "Mi Caja de Chat"
                btn_menu_chat.style = ft.ButtonStyle(bgcolor="#1E232A", color=ft.Colors.WHITE, padding=6)
            page.update()
        except Exception as e:
            print("Error al contar mensajes:", e)

    def cargar_mensajes_chat():
        if not chat_target["paseador_id"]:
            return
        try:
            res = supabase.table("mensajes").select("*").eq("paseador_id", chat_target["paseador_id"]).order("created_at", desc=False).execute()
            mensajes = res.data if res.data else []
            
            chat_mensajes.controls.clear()
            if not mensajes:
                chat_mensajes.controls.append(
                    ft.Container(content=ft.Text("No hay mensajes aún. ¡Escribe el primero!", size=11, color=ft.Colors.GREY_400, italic=True), padding=10)
                )
            else:
                for m in mensajes:
                    remitente = m.get("remitente", "Cliente")
                    texto = m.get("texto", "")
                    es_mio = (remitente == chat_target["remitente_tipo"])
                    
                    chat_mensajes.controls.append(
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"~ {remitente}", size=9, color=ft.Colors.GREY_400 if not es_mio else ft.Colors.WHITE),
                                    ft.Text(texto, size=12, color=ft.Colors.WHITE),
                                ], spacing=2),
                                bgcolor="#4392F1" if es_mio else "#1E232A",
                                padding=8, border_radius=10, width=260,
                                border=None if es_mio else ft.border.all(1, "#2B303A")
                            )
                        ], alignment=ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START)
                    )
            page.update()
        except Exception as e:
            print("Error al cargar chat:", e)

    def enviar_mensaje_db(e):
        texto = txt_mensaje_input.value.strip()
        p_id = chat_target["paseador_id"]
        
        if not texto or not p_id:
            return

        try:
            supabase.table("mensajes").insert({
                "paseador_id": p_id,
                "remitente": chat_target["remitente_tipo"],
                "texto": texto
            }).execute()
            
            txt_mensaje_input.value = ""
            cargar_mensajes_chat()
            threading.Thread(target=actualizar_contador_mensajes).start()
        except Exception as ex:
            print("Error en Supabase:", ex)

    btn_enviar_msg = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="#4392F1", on_click=enviar_mensaje_db)

    vista_interfaz_chat = ft.Column(
        controls=[
            ft.Row([lbl_chat_destino], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color="#2B303A", height=5),
            chat_mensajes,
            ft.Row([txt_mensaje_input, btn_enviar_msg], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], expand=True, spacing=8
    )

    def abrir_chat_con_paseador(e, p_id, p_nombre):
        chat_target["paseador_id"] = p_id
        if paseador_logueado["id"] and paseador_logueado["id"] == p_id:
            chat_target["remitente_tipo"] = f"Paseador ({paseador_logueado['nombre']})"
            lbl_chat_destino.value = "💬 Mi Bandeja de Mensajes"
        else:
            chat_target["remitente_tipo"] = f"Cliente ({paseador_logueado['nombre'] if paseador_logueado['nombre'] else 'Visitante'})"
            lbl_chat_destino.value = f"💬 Chat con {p_nombre}"
            
        if paseador_logueado["id"]:
            dash_contenido.content = vista_interfaz_chat
        else:
            contenido_dinamico.content = vista_interfaz_chat
            
        page.update()
        cargar_mensajes_chat()

    def actualizar_lista_catalogo():
        try:
            response = supabase.table("paseadores").select("*").execute()
            paseadores_registrados = response.data if response.data else []
            
            lista_catalogo.controls.clear()
            if not paseadores_registrados:
                lista_catalogo.controls.append(ft.Text("No hay paseadores inscritos aún.", color=ft.Colors.GREY_400, size=13))
            else:
                for p in paseadores_registrados:
                    p_id = p.get("id")
                    p_nom = p.get("nombre", "Sin nombre")
                    p_zona = p.get("zona", "N/A")
                    p_tarifa = p.get("tarifa", "0")

                    tarjeta = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PETS, color="#4392F1", size=26),
                                ft.Column([
                                    ft.Text(p_nom, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text(f"📍 {p_zona} | 💰 ${p_tarifa}/hr", size=11, color=ft.Colors.GREY_300),
                                ], spacing=2, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.CHAT_BUBBLE_ROUNDED,
                                    icon_color="#4392F1",
                                    on_click=lambda e, id=p_id, nom=p_nom: abrir_chat_con_paseador(e, id, nom)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        bgcolor="#1E232A", padding=10, border_radius=12, border=ft.border.all(1, "#2B303A")
                    )
                    lista_catalogo.controls.append(tarjeta)
            page.update()
        except Exception as e:
            print("Error al cargar catálogo:", e)

    # REGISTRO Y LOGIN
    def procesar_registro(e):
        if not txt_nombre.value or not txt_zona.value or not txt_tarifa.value or not txt_clave_reg.value:
            lbl_resultado_reg.value = "⚠️ Completa todos los campos."
            lbl_resultado_reg.color = ft.Colors.AMBER_400
        else:
            try:
                supabase.table("paseadores").insert({
                    "nombre": txt_nombre.value,
                    "zona": txt_zona.value,
                    "tarifa": txt_tarifa.value,
                    "clave": txt_clave_reg.value
                }).execute()
                lbl_resultado_reg.value = "✅ ¡Cuenta creada con éxito!"
                lbl_resultado_reg.color = ft.Colors.GREEN_400
                txt_nombre.value = ""
                txt_zona.value = ""
                txt_tarifa.value = ""
                txt_clave_reg.value = ""
                threading.Thread(target=actualizar_lista_catalogo).start()
            except Exception as ex:
                lbl_resultado_reg.value = f"⚠️ Error: {ex}"
                lbl_resultado_reg.color = ft.Colors.RED_400
        page.update()

    def procesar_login(e):
        if not txt_login_nombre.value or not txt_login_clave.value:
            lbl_resultado_login.value = "⚠️ Ingresa tu nombre y clave."
            lbl_resultado_login.color = ft.Colors.AMBER_400
        else:
            try:
                res = supabase.table("paseadores").select("*").eq("nombre", txt_login_nombre.value).eq("clave", txt_login_clave.value).execute()
                if res.data:
                    p = res.data[0]
                    paseador_logueado["id"] = p["id"]
                    paseador_logueado["nombre"] = p["nombre"]
                    paseador_logueado["zona"] = p["zona"]
                    paseador_logueado["tarifa"] = p["tarifa"]
                    
                    cargar_dashboard_paseador()
                else:
                    lbl_resultado_login.value = "❌ Nombre o clave incorrectos."
                    lbl_resultado_login.color = ft.Colors.RED_400
            except Exception as ex:
                lbl_resultado_login.value = f"⚠️ Error: {ex}"
                lbl_resultado_login.color = ft.Colors.RED_400
        page.update()

    btn_registrar = ft.ElevatedButton("INSCRIBIRME COMO PASEADOR", on_click=procesar_registro, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#4392F1", padding=14), width=340)
    btn_login = ft.ElevatedButton("INICIAR SESIÓN MI PERFIL", on_click=procesar_login, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#00E676", padding=14), width=340)

    vista_registro_login = ft.Column(
        controls=[
            ft.Text("Registro & Login de Paseadores", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Column([
                    ft.Text("📝 Nuevo Paseador", size=13, weight=ft.FontWeight.BOLD, color="#4392F1"),
                    txt_nombre, txt_zona, txt_tarifa, txt_clave_reg, btn_registrar, lbl_resultado_reg
                ], spacing=6), bgcolor="#1E232A", padding=10, border_radius=10
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("🔑 Ya tengo cuenta", size=13, weight=ft.FontWeight.BOLD, color="#00E676"),
                    txt_login_nombre, txt_login_clave, btn_login, lbl_resultado_login
                ], spacing=6), bgcolor="#1E232A", padding=10, border_radius=10
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, scroll=ft.ScrollMode.AUTO
    )

    vista_catalogo_publico = ft.Column(
        controls=[
            ft.Text("Paseadores Disponibles", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Toca el ícono de chat para coordinar un paseo:", size=11, color=ft.Colors.GREY_400),
            ft.Container(height=5),
            lista_catalogo
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, expand=True
    )

    # DASHBOARD
    lbl_nombre_usuario_header = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color="#00E676")
    dash_contenido = ft.Container(expand=True)

    def ver_paseadores_disponibles(e):
        threading.Thread(target=actualizar_lista_catalogo).start()
        dash_contenido.content = vista_catalogo_publico
        page.update()

    def ver_recomendaciones(e):
        dash_contenido.content = ft.Column([
            ft.Text("💡 Recomendaciones para Paseadores", size=14, weight=ft.FontWeight.BOLD, color="#4392F1"),
            ft.Text("• Revisa la temperatura del asfalto antes de salir.", size=12, color=ft.Colors.WHITE),
            ft.Text("• Lleva siempre agua fresca y recipientes portátiles.", size=12, color=ft.Colors.WHITE),
            ft.Text("• Mantén al día la desparasitación y usa arnés seguro.", size=12, color=ft.Colors.WHITE),
        ], spacing=10, padding=10)
        page.update()

    def ver_info_personal(e):
        dash_contenido.content = ft.Column([
            ft.Text("👤 Información de tu Perfil", size=14, weight=ft.FontWeight.BOLD, color="#4392F1"),
            ft.Text(f"Nombre: {paseador_logueado['nombre']}", size=13, color=ft.Colors.WHITE),
            ft.Text(f"Zona de Trabajo: {paseador_logueado['zona']}", size=13, color=ft.Colors.WHITE),
            ft.Text(f"Tarifa por Hora: ${paseador_logueado['tarifa']}", size=13, color=ft.Colors.GREEN_400),
        ], spacing=10, padding=10)
        page.update()

    def ver_mi_caja_mensajes(e):
        abrir_chat_con_paseador(e, paseador_logueado["id"], paseador_logueado["nombre"])

    def cerrar_sesion(e):
        paseador_logueado["id"] = None
        paseador_logueado["nombre"] = ""
        txt_login_nombre.value = ""
        txt_login_clave.value = ""
        lbl_resultado_login.value = ""
        
        card_principal.content = layout_principal
        page.update()

    btn_menu_paseadores = ft.ElevatedButton("Paseadores", icon=ft.Icons.LIST, on_click=ver_paseadores_disponibles, style=ft.ButtonStyle(bgcolor="#1E232A", color=ft.Colors.WHITE, padding=6))
    btn_menu_recom = ft.ElevatedButton("Consejos", icon=ft.Icons.LIGHTBULB, on_click=ver_recomendaciones, style=ft.ButtonStyle(bgcolor="#1E232A", color=ft.Colors.WHITE, padding=6))
    btn_menu_info = ft.ElevatedButton("Mi Perfil", icon=ft.Icons.PERSON, on_click=ver_info_personal, style=ft.ButtonStyle(bgcolor="#1E232A", color=ft.Colors.WHITE, padding=6))
    btn_menu_chat = ft.ElevatedButton("Mi Caja de Chat", icon=ft.Icons.CHAT, on_click=ver_mi_caja_mensajes, style=ft.ButtonStyle(bgcolor="#1E232A", color=ft.Colors.WHITE, padding=6))
    btn_cerrar_sesion = ft.ElevatedButton("Cerrar cuenta", icon=ft.Icons.LOGOUT, on_click=cerrar_sesion, style=ft.ButtonStyle(bgcolor="#FF5252", color=ft.Colors.WHITE, padding=6))

    menu_dashboard_fila = ft.Row(
        controls=[btn_menu_paseadores, btn_menu_chat, btn_menu_info, btn_menu_recom],
        scroll=ft.ScrollMode.AUTO,
        spacing=6
    )

    def cargar_dashboard_paseador():
        lbl_nombre_usuario_header.value = f"🐾 {paseador_logueado['nombre']}"
        threading.Thread(target=actualizar_contador_mensajes).start()
        ver_mi_caja_mensajes(None)
        
        dashboard_layout = ft.Column([
            ft.Row([
                lbl_nombre_usuario_header,
                btn_cerrar_sesion
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color="#2B303A", height=8),
            menu_dashboard_fila,
            ft.Divider(color="#2B303A", height=8),
            dash_contenido
        ], expand=True, spacing=5)
        
        card_principal.content = dashboard_layout
        page.update()

    contenido_dinamico.content = vista_registro_login

    def cambiar_vista_tab(e, vista_elegida):
        if vista_elegida == "reg":
            contenido_dinamico.content = vista_registro_login
            btn_tab_reg.bgcolor = "#4392F1"
            btn_tab_cat.bgcolor = "#1E232A"
        elif vista_elegida == "cat":
            threading.Thread(target=actualizar_lista_catalogo).start()
            contenido_dinamico.content = vista_catalogo_publico
            btn_tab_cat.bgcolor = "#4392F1"
            btn_tab_reg.bgcolor = "#1E232A"
        page.update()

    btn_tab_reg = ft.ElevatedButton(text="Cuenta / Login", icon=ft.Icons.LOCK, on_click=lambda e: cambiar_vista_tab(e, "reg"), style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#4392F1", padding=10))
    btn_tab_cat = ft.ElevatedButton(text="Paseadores", icon=ft.Icons.LIST, on_click=lambda e: cambiar_vista_tab(e, "cat"), style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#1E232A", padding=10))

    barra_navegacion = ft.Row(controls=[btn_tab_reg, btn_tab_cat], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    cabecera_principal = ft.Column(
        controls=[
            ft.Row([
                ft.Container(content=ft.Image(src="perro.gif", width=45, height=45, fit=ft.ImageFit.CONTAIN), bgcolor="#87CEEB", padding=5, border_radius=12),
                ft.Image(src="patitas_titulo.png", width=150, height=30, fit=ft.ImageFit.CONTAIN),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Divider(color="#2B303A", height=8),
            barra_navegacion,
            ft.Divider(color="#2B303A", height=8),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4
    )

    layout_principal = ft.Column([cabecera_principal, contenido_dinamico], expand=True)

    card_principal = ft.Container(
        content=layout_principal,
        width=390, height=760, padding=15, bgcolor="#181B20", border_radius=18, border=ft.border.all(1, "#2B303A")
    )

    page.add(card_principal)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")