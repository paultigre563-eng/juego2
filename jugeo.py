
import streamlit as st
import random
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Candy World",
    page_icon="🍬",
    layout="wide"
)

# -----------------------------
# ESTILOS
# -----------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#25115c,#6d258d,#e34b9b);
    color: white;
}
header, footer {
    visibility: hidden;
}
.block-container {
    padding-top: 1rem;
}
h1 {
    text-align: center;
    color: #ffe77a;
    font-size: 48px !important;
    text-shadow: 0 4px 8px #32104f;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CONFIGURACIÓN
# -----------------------------

FILAS = 8
COLUMNAS = 8

CARAMELOS = ["🍬", "🍭", "🍒", "🍋", "🍇", "🍉"]

COLORES = {
    "🍬": "#ff4b91",
    "🍭": "#ffcc38",
    "🍒": "#e72e43",
    "🍋": "#ffe33d",
    "🍇": "#a34ce0",
    "🍉": "#35c97b"
}

# -----------------------------
# FUNCIONES DEL JUEGO
# -----------------------------

def crear_tablero():
    tablero = []

    for f in range(FILAS):
        fila = []

        for c in range(COLUMNAS):
            opciones = CARAMELOS.copy()

            while True:
                caramelo = random.choice(opciones)

                if c >= 2 and fila[c-1] == caramelo and fila[c-2] == caramelo:
                    opciones.remove(caramelo)
                    continue

                if f >= 2 and tablero[f-1][c] == caramelo and tablero[f-2][c] == caramelo:
                    opciones.remove(caramelo)
                    continue

                break

            fila.append(caramelo)

        tablero.append(fila)

    return tablero


def encontrar_combinaciones(tablero):
    combinaciones = set()

    # Horizontales
    for f in range(FILAS):
        for c in range(COLUMNAS-2):

            if (
                tablero[f][c] is not None
                and tablero[f][c] == tablero[f][c+1]
                and tablero[f][c] == tablero[f][c+2]
            ):
                combinaciones.update({
                    (f,c), (f,c+1), (f,c+2)
                })

                k = c+3

                while k < COLUMNAS and tablero[f][k] == tablero[f][c]:
                    combinaciones.add((f,k))
                    k += 1

    # Verticales
    for f in range(FILAS-2):
        for c in range(COLUMNAS):

            if (
                tablero[f][c] is not None
                and tablero[f][c] == tablero[f+1][c]
                and tablero[f][c] == tablero[f+2][c]
            ):
                combinaciones.update({
                    (f,c), (f+1,c), (f+2,c)
                })

                k = f+3

                while k < FILAS and tablero[k][c] == tablero[f][c]:
                    combinaciones.add((k,c))
                    k += 1

    return combinaciones


def eliminar_combinaciones(tablero):
    combinaciones = encontrar_combinaciones(tablero)

    for f,c in combinaciones:
        tablero[f][c] = None

    return len(combinaciones)


def aplicar_gravedad(tablero):
    for c in range(COLUMNAS):

        columna = []

        for f in range(FILAS):
            if tablero[f][c] is not None:
                columna.append(tablero[f][c])

        faltantes = FILAS-len(columna)

        nuevos = [
            random.choice(CARAMELOS)
            for _ in range(faltantes)
        ]

        nueva_columna = nuevos+columna

        for f in range(FILAS):
            tablero[f][c] = nueva_columna[f]


def resolver_tablero(tablero):
    total = 0

    while True:
        eliminados = eliminar_combinaciones(tablero)

        if eliminados == 0:
            break

        total += eliminados
        aplicar_gravedad(tablero)

    return total


def intercambiar(tablero, a, b):
    fa,ca = a
    fb,cb = b

    tablero[fa][ca], tablero[fb][cb] = (
        tablero[fb][cb],
        tablero[fa][ca]
    )


def adyacentes(a,b):
    return (
        abs(a[0]-b[0]) +
        abs(a[1]-b[1])
    ) == 1


# -----------------------------
# ESTADO DEL JUEGO
# -----------------------------

if "tablero" not in st.session_state:
    st.session_state.tablero = crear_tablero()
    st.session_state.puntos = 0
    st.session_state.movimientos = 25
    st.session_state.nivel = 1
    st.session_state.seleccion = None
    st.session_state.mensaje = "¡Combina 3 o más caramelos!"
    st.session_state.meta = 500


def nuevo_juego():
    st.session_state.tablero = crear_tablero()
    st.session_state.puntos = 0
    st.session_state.movimientos = 25
    st.session_state.nivel = 1
    st.session_state.seleccion = None
    st.session_state.mensaje = "¡Empieza a jugar!"
    st.session_state.meta = 500


def seleccionar(f,c):
    tablero = st.session_state.tablero

    if st.session_state.movimientos <= 0:
        st.session_state.mensaje = "¡No quedan movimientos!"
        return

    actual = (f,c)
    anterior = st.session_state.seleccion

    if anterior is None:
        st.session_state.seleccion = actual
        st.session_state.mensaje = "Selecciona un caramelo vecino."
        return

    if anterior == actual:
        st.session_state.seleccion = None
        return

    if not adyacentes(anterior,actual):
        st.session_state.seleccion = actual
        st.session_state.mensaje = "Selecciona una pieza vecina."
        return

    intercambiar(tablero,anterior,actual)

    combinaciones = encontrar_combinaciones(tablero)

    if not combinaciones:
        intercambiar(tablero,anterior,actual)
        st.session_state.mensaje = "¡Ese movimiento no forma una combinación!"
    else:
        cantidad = resolver_tablero(tablero)

        puntos = cantidad*30

        st.session_state.puntos += puntos
        st.session_state.movimientos -= 1

        st.session_state.mensaje = (
            f"¡Excelente! +{puntos} puntos"
        )

        if st.session_state.puntos >= st.session_state.meta:
            st.session_state.nivel += 1
            st.session_state.meta += 500
            st.session_state.movimientos += 10
            st.session_state.mensaje = (
                f"¡NIVEL {st.session_state.nivel} COMPLETADO!"
            )

    st.session_state.seleccion = None


# -----------------------------
# INTERFAZ
# -----------------------------

st.markdown("<h1>🍬 CANDY WORLD 🍭</h1>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;color:#ffe8ff;'>"
    "¡Intercambia caramelos, crea combinaciones y consigue puntos!"
    "</p>",
    unsafe_allow_html=True
)

a,b,c,d = st.columns(4)

a.metric("⭐ PUNTOS",st.session_state.puntos)
b.metric("🎯 META",st.session_state.meta)
c.metric("❤️ MOVIMIENTOS",st.session_state.movimientos)
d.metric("🏆 NIVEL",st.session_state.nivel)

st.progress(
    min(
        st.session_state.puntos/st.session_state.meta,
        1.0
    )
)

st.markdown("---")

st.markdown(
    f"<h3 style='text-align:center;color:#ffe77a;'>"
    f"{st.session_state.mensaje}</h3>",
    unsafe_allow_html=True
)

# -----------------------------
# TABLERO
# -----------------------------

tablero = st.session_state.tablero

for f in range(FILAS):

    columnas = st.columns(COLUMNAS,gap="small")

    for c in range(COLUMNAS):

        caramelo = tablero[f][c]

        seleccionado = (
            st.session_state.seleccion == (f,c)
        )

        color = COLORES[caramelo]

        borde = "5px solid white" if seleccionado else "2px solid rgba(255,255,255,.35)"

        with columnas[c]:

            st.markdown(
                f"""
                <div style="
                    background:linear-gradient(145deg,{color},#ffffff33);
                    border:{borde};
                    border-radius:13px;
                    height:53px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:27px;
                    box-shadow:0 4px 8px #180b38;
                    margin-bottom:3px;
                ">
                {caramelo}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                " ",
                key=f"pieza_{f}_{c}",
                use_container_width=True
            ):
                seleccionar(f,c)
                st.rerun()

# -----------------------------
# BOTONES
# -----------------------------

st.markdown("---")

col1,col2,col3 = st.columns(3)

with col1:
    if st.button("🔄 NUEVA PARTIDA",use_container_width=True):
        nuevo_juego()
        st.rerun()

with col2:
    if st.button("🎲 MEZCLAR TABLERO",use_container_width=True):
        st.session_state.tablero = crear_tablero()
        st.session_state.seleccion = None
        st.session_state.mensaje = "¡Tablero mezclado!"
        st.rerun()

with col3:
    if st.button("❔ CÓMO JUGAR",use_container_width=True):
        st.session_state.mensaje = (
            "Selecciona dos caramelos vecinos para intercambiarlos."
        )
        st.rerun()

if st.session_state.movimientos <= 0:
    st.error("¡FIN DE LA PARTIDA! Pulsa NUEVA PARTIDA para volver a jugar.")
