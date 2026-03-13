# 📈 COLCAP Dashboard

Dashboard interactivo de acciones del índice COLCAP de la Bolsa de Valores de Colombia.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## ✨ Funcionalidades

- **19 acciones COLCAP** + índice `^COLCAP`
- **Período personalizable**: 1 mes · 3 meses · 6 meses · 1 año · 2 años · 5 años · rango libre
- **Filtro por sector**: Energía · Financiero · Industrial · Consumo · Materiales · Telecom
- **Gráfico base 100** para comparar rendimientos relativos
- **Retorno del período** y **volatilidad anualizada** por acción
- **Matriz de correlación** de retornos diarios
- **Tabla resumen** con precio actual, máximos, mínimos, sesiones
- **Exportar CSV** de precios y resumen estadístico
- Datos en tiempo real via **Yahoo Finance** (caché 15 min)

## 🚀 Correr localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📦 Deploy en Streamlit Cloud

1. Sube este repo a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Nuevo app → selecciona tu repo → `streamlit_app.py`
4. Deploy ✅

## 🏢 Acciones incluidas

| Acción | Ticker BVC | Sector |
|--------|-----------|--------|
| COLCAP (Índice) | ^COLCAP | Índice |
| Ecopetrol | ECOPETL.CL | Energía |
| Bancolombia | BCOLO.CL | Financiero |
| Pref. Bancolombia | PFBCOLO.CL | Financiero |
| Grupo Sura | GRUPOSURA.CL | Financiero |
| Grupo Argos | GRUPOARGOS.CL | Industrial |
| Cementos Argos | CEMARGOS.CL | Industrial |
| Nutresa | NUTRESA.CL | Consumo |
| ISA | ISA.CL | Energía |
| GEB | GEB.CL | Energía |
| Celsia | CELSIA.CL | Energía |
| Mineros | MINEROS.CL | Materiales |
| Canacol Energy | CNE.TO | Energía |
| Corficolombiana | CORFICOLCF.CL | Financiero |
| Promigas | PROMIGAS.CL | Energía |
| ETB | ETB.CL | Telecom |
| Almacenes Éxito | EXITO.CL | Consumo |

## 📄 Licencia

MIT
