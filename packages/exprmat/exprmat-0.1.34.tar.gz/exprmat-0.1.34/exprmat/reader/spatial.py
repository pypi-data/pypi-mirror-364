
import anndata as ad
import pandas as pd
import numpy as np
import os

from exprmat.reader.metadata import metadata
from exprmat.ansi import error, warning


def read_table(prefix, **kwargs):

    if os.path.isfile(prefix + '.parquet'):
        return pd.read_parquet(prefix + '.parquet', **kwargs)
    elif os.path.isfile(prefix + '.parquet.gz'):
        return pd.read_parquet(prefix + '.parquet.gz', **kwargs)
    elif os.path.isfile(prefix + '.feather'):
        return pd.read_feather(prefix + '.feather', **kwargs)
    elif os.path.isfile(prefix + '.feather.gz'):
        return pd.read_feather(prefix + '.feather.gz', **kwargs)
    elif os.path.isfile(prefix + '.tsv'):
        return pd.read_table(prefix + '.tsv', **kwargs)
    elif os.path.isfile(prefix + '.tsv.gz'):
        return pd.read_table(prefix + '.tsv.gz', **kwargs)
    elif os.path.isfile(prefix + '.csv'):
        return pd.read_csv(prefix + '.csv', **kwargs)
    elif os.path.isfile(prefix + '.csv.gz'):
        return pd.read_csv(prefix + '.csv.gz', **kwargs)
    else: error(f'do not find {prefix} in any supported table format.')


def read_multiscale_image(basefile, l_highres = 2, l_lowres = 4):

    basefn = os.path.basename(basefile)
    basefull, baseext = os.path.splitext(basefile)
    basefn = basefn[:-len(baseext)]

    # tiff files
    if basefile.endswith('.gz'):
        import sh
        sh.gunzip(basefile)
        basefile = basefile[:-3]
    
    if basefile.endswith('.ome.tif') or basefile.endswith('.ome.tiff'):
        import tifffile
        # fullres_multich_img = tifffile.imread(
        #     basefile, is_ome = True, level = 0, aszarr = False)
        highres = tifffile.imread(basefile, is_ome = False, level = l_highres)
        lowres = tifffile.imread(basefile, is_ome = False, level = l_lowres)
        
        return {
            'images': {
                'hires': highres,
                'lores': lowres,
                'origin': basefile
            },
            'scalefactors': {
                'hires': 1 / (2 ** l_highres),
                'lores': 1 / (2 ** l_lowres),
                'origin': 1
            },
            'mask': None,
            'segmentation': None
        }
    
    elif (
        os.path.exists(basefull + '.hires' + baseext) and
        os.path.exists(basefull + '.lores' + baseext)
    ):
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = 5000000000
        # set a max limit to 10000 * 50000 px.

        highres = Image.open(basefull + '.hires' + baseext)
        lowres = Image.open(basefull + '.lores' + baseext)

        sp = {
            'images': {
                'hires': np.array(highres),
                'lores': np.array(lowres),
                'origin': basefile
            },
            'scalefactors': {
                'hires': 1 / (2 ** l_highres),
                'lores': 1 / (2 ** l_lowres),
                'origin': 1
            },
            'mask': None,
            'segmentation': None
        }

        highres.close()
        lowres.close()
        return sp
    
    else: # handle and downsample them using pillow

        from PIL import Image
        Image.MAX_IMAGE_PIXELS = 5000000000

        fullres_multich_img = Image.open(basefile)

        w, h = fullres_multich_img.size
        highres = fullres_multich_img.resize((w // int(2 ** l_highres), h // int(2 ** l_highres)))
        lowres = fullres_multich_img.resize((w // int(2 ** l_lowres), h // int(2 ** l_lowres)))
        
        highres.save(basefull + '.hires' + baseext)
        lowres.save(basefull + '.lores' + baseext)

        sp = {
            'images': {
                'hires': np.array(highres),
                'lores': np.array(lowres),
                'origin': basefile
            },
            'scalefactors': {
                'hires': 1 / (2 ** l_highres),
                'lores': 1 / (2 ** l_lowres),
                'origin': 1
            },
            'mask': None,
            'segmentation': None
        }

        highres.close()
        lowres.close()
        fullres_multich_img.close()
        return sp


def read_seekspace(
    src: str, prefix: str, 
    metadata: metadata, sample: str, raw: bool = False,
    default_taxa = 'mmu', eccentric = None
):

    from exprmat.reader.matcher import read_mtx_rna
    adata = read_mtx_rna(
        src, prefix, metadata = metadata, sample = sample, raw = raw,
        default_taxa = default_taxa, eccentric = eccentric
    )

    # attach morphology
    rows = metadata.dataframe[metadata.dataframe['sample'] == sample]
    assert len(rows) >= 1
    rows = rows[rows['modality'] == 'rnasp-c']
    assert len(rows) == 1
    props = rows.iloc[0]

    # tiff files are high quality files.
    if os.path.exists(os.path.join(src, 'morphology.tiff')):
        adata.uns['spatial'] = {
            props['sample']: read_multiscale_image(os.path.join(src, 'morphology.tiff'))
        }
    
    # png files are considered low-quality files without full resolution.
    elif os.path.exists(os.path.join(src, 'morphology.png')):
        adata.uns['spatial'] = {
            props['sample']: read_multiscale_image(os.path.join(src, 'morphology.png'), 0, 1)
        }

    # attach spatial coordinates
    spatial = read_table(os.path.join(src, 'cell_locations'), index_col = 0)
    barcodes = adata.obs['barcode'].tolist()
    spatial.index = (props['sample'] + ':') + spatial.index
    sorted_df = spatial.loc[barcodes, :].copy()
    sorted_df.columns = ['x', 'y']
    adata.obsm['spatial'] = sorted_df.values

    return adata

