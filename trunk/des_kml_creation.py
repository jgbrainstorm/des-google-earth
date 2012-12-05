#! /usr/bin/env python

#----------------------------------------------------#
# This python script will generate the kml files with 
# your own images as in:
# https://sites.google.com/site/geclusters/
# Depencency:
# 1. wcs2kml
# 2. python

# usage: 
# 1. you need to have the fits file as well as the corresponding 
# color png files available. Put them into separate directories
# see the make_kml_image() function for example, replace the directories

# 2.In the make_kml_image() function, you need to specify the 
# pngDIR, fitsDIR, kmlDIR, kmlNAME,regionateDIR     

# 3. In the make_root_kml function, you need to specify:
# kmlDIR, kmlNAME and the name of your final root kml. All the names need 
# to be consistent with the ones set in make_kml_image() function

#-----------------------------------------------------#
# If you use this codes, acknowledgements are appreciated. 
# You can make reference to: http://arxiv.org/abs/1010.6068

# Contact: Jiangang Hao, jghao@fnal.gov for help. 

# Jiangang Hao @ FermiLab, 10/19/2009


import glob as gl
import os


def make_kml_image(pngDIR = None,fitsDIR = None,kmlDIR = None,regionate = True):
    """ 
    this crate the hiachy of dir and warped images
    """
    pngNAME = gl.glob(pngDIR+'*.png')
    fitsNAME = gl.glob(fitsDIR+'*.fits')
    pngNAME.sort()
    fitsNAME.sort()
    num = len(pngNAME)
    wcs2kmldir='/home/jghao/research/ggsvn/des-google-earth/wcs2kml_install/bin/'
    for i in range(0,num):
        kmlNAME = kmlDIR+pngNAME[i][-17:-4]+'.kml'
        if regionate == True:
            regionateDIR=kmlDIR+pngNAME[i][-17:-4]
            comand = wcs2kmldir+'wcs2kml --imagefile='+pngNAME[i]+' --fitsfile='+fitsNAME[i]+' --kmlfile='+kmlNAME+' --regionate'+' --regionate_dir='+regionateDIR+' --input_image_origin_is_upper_left=true --regionate_min_lod_pixels=0'
        else:
            comand = wcs2kmldir+'wcs2kml --imagefile='+pngNAME[i]+' --fitsfile='+fitsNAME[i]+' --kmlfile='+kmlNAME+' --outfile='+kmlDIR+pngNAME[i][-13:-4]+'wrap.png'
        os.system(comand)
    print("---The End----")
    return(0)


def make_root_kml(kmlDIR = None):
    """ 
    This function create the root kml file
    """
    kmlNAME = gl.glob(kmlDIR+'*.kml')
    kmlNAME.sort()
    num = len(kmlNAME)
    kml=open('des_ge_fnal_patch2_hao.kml','w')
    kml.write('<?xml version="1.0" encoding="UTF-8"?> \n')
    kml.write('<kml xmlns="http://earth.google.com/kml/2.2" hint="target=sky"> \n')
    kml.write('<Document>\n')
    for i in range(0,num): 
        f = open(kmlNAME[i],'r')
        line = f.readlines()
        for j in range(3,20):
            kml.write(line[j])
        f.close()
    kml.write('</Document>\n')
    kml.write('</kml>\n')
    kml.close()
    return(0)

def rescale_png():
    """
    this one reduce the size of the png files. It is not needed if you want to use the full resolution.
    """
    kmlDIR = 'somewhere/kmlfile/'
    kmlNAME = gl.glob(kmlDIR+'fpC*.kml')
    kmlNAME.sort()
    num = len(kmlNAME)
    for i in range(0,num):
        print(i)
        subdir = kmlDIR+kmlNAME[i][47:68]+'/'
        pngNAME = gl.glob(subdir+'*.png')
        numsub = len(pngNAME)
        for j in range(0,numsub):
            comand = 'convert -resize 50%x50% -unsharp 0 '+pngNAME[j]+' '+pngNAME[j]
            os.system(comand)

def download_file(run=None,camcol=None):
    """
    This function download images to your working directory. You do not need it
    """

    pngDIR = 'somewhere/pngfile/'
    fitsDIR = 'somewhere/fitsfile/'
 
    fits = 'somewhere/data/annis/Coadd/corr/'+run+'/'+camcol+'/*RGB*.fits'
    png = 'somewhere/data/annis/Coadd/corr/'+run+'/'+camcol+'/*RGB*.png'
    os.system('scp -r '+fits+' '+fitsDIR)
    os.system('scp -r '+png+' '+pngDIR)
    return(0)


def remove_file():
    """
    This will remove the png and fits files. You do not want to use it if you want to keep your original copies.
    """
    pngDIR = 'somewhere/pngfile/'
    fitsDIR = 'somewhere/fitsfile/'

    os.system('rm '+pngDIR+'*.png')
    os.system('rm '+fitsDIR+'*.fits')
    return(0)
 
     
if __name__ == "__main__":
    
    from des_kml_creation import *

    #--- make color png file from fits file ---
    
    # ---this is optional. skip it if you want the full resolution images---
    step1 = rescale_png() 

    #----make kml and warped images
    pngDIR = '/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/medium/gri/'
    fitsDIR = '/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/medium/'

    kmlDIR = '/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/medium/gri/kml/'

    
    step2=make_kml_image(pngDIR,fitsDIR,kmlDIR)

    #----make the final kml file -----
    step3=make_root_kml(kmlDIR)
