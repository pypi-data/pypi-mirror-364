import npsam as ns
from numpy import inf

files = [
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 0840 380 kx 266 nm.emd',
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 0859 520 kx 192 nm.emd',
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 0955 520 kx 192 nm.emd',
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 1217 380 kx 266 nm 0001.emd',
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 1307 740 kx 136 nm.emd',
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 1309 190 kx 532 nm.emd',
    '../../paper/figures/fig4_PdCu/data/N2/STEM HAADF-DF4-DF2-BF 1313 265 kx 376 nm.emd',
]
s = ns.NPSAM(files, select_image='HAADF')

s.set_scaling([
    '0.2599492959418759 nm',
    '0.18721313549784396 nm',
    '0.18721313549784396 nm',
    '0.2599492959418759 nm',
    '0.1323796776377215 nm',
    '0.5198985918837518 nm',
    '0.36762381985033804 nm',
])

s.segment(
    SAM_model='fast',
    PPS = 64,
    shape_filter = True,
    edge_filter = True,
    crop_and_enlarge = False,
    invert = False,
    double = False,
    min_mask_region_area = 100,
)

