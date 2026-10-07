import streamlit as st
from PIL import Image
from vectorise import load_rgb_on_white, trace, evaluate

st.set_page_config(page_title="Logo vectoriser")
st.title("Raster → SVG, with a quality report")
st.write("Trace a logo, then see how faithful and how editable the result is.")

file = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
cp = st.slider("Colour precision", 1, 8, 6)
fs = st.slider("Speckle filter", 0, 20, 4)
ct = st.slider("Corner threshold", 0, 180, 60, step=5)

if file is not None:
    orig = load_rgb_on_white(Image.open(file))
    svg = trace(orig, cp, fs, ct)
    stats, rendered = evaluate(orig, svg)

    c1, c2 = st.columns(2)
    c1.image(orig, caption="Original")
    c2.image(rendered, caption="SVG re-rendered")

    st.subheader("Report")
    st.json(stats)
    if stats["nodes"] > 1500:
        st.warning("Over 1500 nodes: a designer would struggle to edit this.")

    st.download_button("Download SVG", svg, file_name="logo.svg", mime="image/svg+xml")
    with st.expander("SVG source"):
        st.code(svg[:3000], language="xml")
