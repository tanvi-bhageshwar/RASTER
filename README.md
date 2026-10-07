Logo vectoriser: raster → SVG, with a fidelity and editability report

Live demo: https://imagecon.streamlit.app (the free tier sleeps when idle; click to wake it)

Designers need logos as editable vector files, but most logos arrive as PNG or JPG. Tracing tools convert one to the other, and the usual check is "does it look the same?" That is not enough: a trace can look identical and still be a pile of hundreds of tiny shapes nobody wants to edit.

This project traces a logo to SVG and then measures two things separately:

Fidelity: does the SVG still look like the original?
Editability: how many shapes, nodes and colours does a designer have to deal with?
What it does
Flattens transparency onto white and resizes to at most 512 px.
Traces the image to SVG with VTracer.
Re-renders the SVG to pixels with resvg and compares it to the original.
Reports SSIM, mean absolute error, paths, nodes, colours and file size.
Warns when a trace goes above 1,500 nodes.
What I built (and what I didn't)
Not mine: the tracing. VTracer does that.
Mine:
vectorise.py: the pipeline, including evaluate() (re-render and compare) and svg_stats() (counts paths, nodes and colours by parsing the SVG).
streamlit_app.py: the demo, with live sliders for the tracing settings.
evaluate.py: batch runner that writes results.csv.
The experiments and conclusions below.
Metrics
Metric	Meaning
SSIM	Structural similarity of original vs re-rendered SVG (1.0 = identical)
Mean abs. error	Average per-pixel colour difference (0 = identical)
Paths	Number of separate shapes
Nodes	Approximate count of drawing commands, i.e. how much a designer has to manage
Colours	Distinct fill colours
Experiment: one gradient logo, five settings

Test image: a multi-colour gradient bird, 225×225. Same image every run; only the sliders changed.

Colour precision	Speckle filter	Corner threshold	SSIM	Mean abs. err	Paths	Nodes	Colours	SVG size
6 (default)	4	60	0.9361	—	183	1,798	183	122.5 KB
5	2	0	0.9366	3.95	186	1,357	186	80.3 KB
5	2	180	0.9296	4.25	186	1,712	186	114.3 KB
4	4	65	0.9225	4.82	63	763	63	51.9 KB
3	10	60	0.9227	4.81	63	759	63	51.8 KB
Findings

1. SSIM barely moves while editability changes a lot. Across all five runs SSIM stays within 0.9225 to 0.9366, a spread of about 0.014. Over the same runs, nodes range from 759 to 1,798, a factor of roughly 2.4. If I had picked settings by SSIM alone, I could not have told a 759-node file from a 1,798-node one. Fidelity metrics alone are a poor guide to whether the output is usable.

2. Colour precision acts like a step, not a dial. Going from precision 5 to 4 cut colours from 186 to 63 and nodes from about 1,360–1,710 to about 760, for a cost of roughly 0.014 SSIM. Going from precision 4 to 3 (with speckle 4 → 10) changed essentially nothing: 763 vs 759 nodes. Precision 6 and 5 also behave almost the same (183 vs 186 colours). On this logo, the useful range of that setting is narrow.

3. Corner threshold changed output size noticeably, in a direction I didn't expect. At precision 5 and speckle 2, going from corner threshold 0 to 180 raised nodes from 1,357 to 1,712 (+26%) and file size from 80 KB to 114 KB (+42%), while SSIM fell from 0.9366 to 0.9296. On this logo, threshold 0 was better on every measure. I have not investigated why, and one logo is not enough to generalise from.

4. Gradients are the underlying problem. VTracer produces flat fills, so a smooth gradient has to be approximated with many small patches of flat colour. That is why the default run has 183 paths and 183 colours (one colour per path). A designer would expect a few shapes with gradient fills. In the re-render, the soft blotchy patches on the feathers are where the flat regions meet.

5. Small detail: the first path in the output is a full-canvas rectangle, the white background traced as a shape. A designer would delete it. Stripping it automatically would be an easy improvement.

Which settings would I hand a designer?

Of the five runs, I would pick precision 4 / speckle 4 (763 nodes, 63 colours) over precision 5 / speckle 2 / corner 0 (1,357 nodes, 186 colours). It costs about 0.014 SSIM (0.9366 to 0.9225) but nearly halves the nodes and cuts colours by two thirds, which is much less to clean up by hand.

Still to do

- Test on a simple flat logo and on a batch of 15–20 logos. All results above come from one gradient logo.
Output is flat-colour paths only; VTracer does not recover gradients.
Text is traced as shapes, not recovered as editable fonts or letter spacing.
The 1,500-node warning is an arbitrary threshold I chose. It has not been checked with designers.
Every result above comes from a single logo, so the numbers are indicative, not statistical.
SSIM measures pixel similarity, not whether a logo is good. A real evaluation would include human judgement.
Run it
bash
pip install -r requirements.txt
streamlit run streamlit_app.py
python evaluate.py logos      # batch run -> results.csv

Runs on Python 3.12. (A deployment on Python 3.14 crashed with a segmentation fault in the compiled dependencies.)

Stack

Python, VTracer, resvg-py, scikit-image, Pillow, NumPy, Streamlit.
