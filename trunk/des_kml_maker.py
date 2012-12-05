#! /usr/bin/env python

#---this is the final one by coming previous pieces --
from fits2color import *
from des_kml_creation import *

def sliceImg(filename,band):
    nimg = 4
    npix = 14000/4.
    for i in range(nimg):
        for j in range(nimg):
            print i,j
            imghdu= pf.open(filename)
            imghdu[0].data = imghdu[0].data[i*npix:(i+1)*npix,j*npix:(j+1)*npix]
            xdiff = 1750.5+j*npix - 7000.5
            ydiff = 1750.5+i*npix - 7000.5
            imghdu[0].header.update('CRPIX1',1750.5)
            imghdu[0].header.update('CRPIX2',1750.5)
            imghdu[0].header.update('NAXIS1',3500)
            imghdu[0].header.update('NAXIS2',3500)
            crval1 = imghdu[0].header['CRVAL1']
            crval2 = imghdu[0].header['CRVAL2']
            imghdu[0].header.update('CRVAL1',crval1-xdiff*0.27/3600.)
            imghdu[0].header.update('CRVAL2',crval2+ydiff*0.27/3600.)
            imghdu.writeto(dir+'medium/image_'+band+'_'+str(i)+'_'+str(j)+'.fits')


dir = '/home/jghao/research/data/des_realimage/des-google/testfield2/'

redF=dir+'image_i.fits'
greenF=dir+'image_r.fits'
blueF=dir+'image_g.fits'
infraredF=dir+'image_z.fits'

sliceImg(redF,'i')
sliceImg(greenF,'r')
sliceImg(blueF,'g')
sliceImg(infraredF,'z')

def testcontrast(contrast=None,bright = None,size=None,nonlinearity=None):
    i = 1
    j = 2
    redF = dir+'medium/image_z_'+str(i)+'_'+str(j)+'.fits'
    greenF = dir+'medium/image_r_'+str(i)+'_'+str(j)+'.fits'
    blueF = dir+'medium/image_g_'+str(i)+'_'+str(j)+'.fits'
    img=colorImg(redF,greenF,blueF,scale=[0.048*size,0.040*size,0.04*size],nonlinearity=nonlinearity,smooth=1.)
    img = ImageEnhance.Brightness(img)
    img = img.enhance(bright)
    ehImg=ImageEnhance.Contrast(img)
    newImg=ehImg.enhance(contrast)
    newImg.show()



#-----make color image ---
#g,r,z
nimg = 4
for i in range(nimg):
    for j in range(nimg):
        print i,j
        redF = dir+'medium/image_z_'+str(i)+'_'+str(j)+'.fits'
        greenF = dir+'medium/image_r_'+str(i)+'_'+str(j)+'.fits'
        blueF = dir+'medium/image_g_'+str(i)+'_'+str(j)+'.fits'
        size = 0.25
        img=colorImg(redF,greenF,blueF,scale=[0.048*size,0.04*size,0.04*size],nonlinearity=20,smooth=1.)
        img = ImageEnhance.Brightness(img)
        img = img.enhance(1.4)
        img=ImageEnhance.Contrast(img)
        img=img.enhance(1.9)
        img.save(dir+'medium/grz/image_rgb_'+str(i)+'_'+str(j)+'.png')


#----combine back to a large color image-----
blank_image = Image.new('RGB',(14000,14000))
nimg = 4
npix=3500
for i in range(nimg):
    for j in range(nimg):
        print i,j
        colimg = dir+'medium/grz/image_rgb_'+str(i)+'_'+str(j)+'.png'
        im = Image.open(colimg)
        blank_image.paste(im,(j*npix,i*npix))
        blank_image.save(dir+'des_coadd_newfield_1deg_grz.png')
 


pngDIR = '/home/jghao/research/data/des_realimage/des-google/testfield2/medium/grz/'
fitsDIR = '/home/jghao/research/data/des_realimage/des-google/testfield2/medium/'
kmlDIR = '/home/jghao/research/data/des_realimage/des-google/testfield2/medium/grz/kml/'

step2=make_kml_image(pngDIR,fitsDIR,kmlDIR)
step3=make_root_kml(kmlDIR)
